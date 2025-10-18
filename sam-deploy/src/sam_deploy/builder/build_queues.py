from sam_deploy.config.mapping import QueueProperty, ENVIRONMENT, Region, LambdaName
from sam_deploy.builder.template_builder import TemplateBuilder


class QueueBuilder:
    builder: TemplateBuilder

    def __init__(self, builder: TemplateBuilder) -> None:
        self.builder = builder

    def build_queue(self, queue_config: QueueProperty, env: ENVIRONMENT) -> dict[str, dict]:
        """
        Creates SQS queue and Dead Letter Queue resources for a given queue configuration.

        Args:
            queue_config: Queue property containing name, roles, visibility timeout, etc.
            env: Environment (DEV, STAGING, PROD, LOCAL)

        Returns:
            Dictionary of CloudFormation resources (main queue and DLQ)
        """
        resources = {}

        # Generate queue names
        main_queue_name = self.builder.getQueueName(queue_config.name, 'Q')
        dlq_name = self.builder.getQueueName(queue_config.name, 'DLQ')

        # Create Dead Letter Queue
        resources[dlq_name] = self.builder.createDLQ(dlq_name)

        # Create main queue with DLQ reference
        resources[main_queue_name] = self.builder.createQ(main_queue_name, dlq_name)

        # Add optional policy if specified
        if queue_config.policy:
            resources[f'{queue_config.name.value}Policy'] = queue_config.policy

        return resources

    def build_event_source_mapping(
        self,
        queue_config: QueueProperty,
        env: ENVIRONMENT,
        function_name: LambdaName
    ) -> dict[str, dict]:
        """
        Creates EventSourceMapping for Lambda-SQS integration.
        Skips creation for LOCAL environment.

        Args:
            queue_config: Queue property containing name and configuration
            env: Environment (DEV, STAGING, PROD, LOCAL)
            function_name: Lambda function enum name to attach to queue

        Returns:
            Dictionary with EventSourceMapping resource, or empty dict for LOCAL
        """
        # Skip EventSourceMapping for LOCAL environment
        if env == ENVIRONMENT.LOCAL:
            return {}

        resources = {}
        main_queue_name = self.builder.getQueueName(queue_config.name, 'Q')
        event_mapping_name = self.builder.getQueueName(queue_config.name, 'EventSourceMapping')

        # Create EventSourceMapping using builder helper
        resources[event_mapping_name] = self.builder.createQEventMapping(
            main_queue_name,
            self.builder.getFunctionName(function_name)
        )

        return resources

    def execute(
        self,
        lambda_name: LambdaName,
        queues: list[QueueProperty],
        region: Region
    ) -> None:
        """
        Builds all queues and event source mappings for all 4 environments.
        Creates queues for DEV, STAGING, PROD, and LOCAL.
        Creates EventSourceMapping only for non-LOCAL environments.

        Args:
            lambda_name: Lambda function name to attach queues to
            queues: List of queue configurations
            region: AWS region
        """
        for queue_config in queues:
            # Build queue resources (Q and DLQ) for current environment
            queue_resources = self.build_queue(queue_config, self.builder.env)
            self.builder.resources.update(queue_resources)

            # Build EventSourceMapping (skipped for LOCAL)
            event_source_resources = self.build_event_source_mapping(
                queue_config,
                self.builder.env,
                lambda_name
            )
            self.builder.resources.update(event_source_resources)

            # Handle API Gateway SQS triggers if configured
            if queue_config.apiTrigger:
                paths = self._add_sqs_path_to_api_gateway(queue_config)
                if self.builder.getApiGatewayName() in self.builder.resources:
                    api_gateway = self.builder.resources[self.builder.getApiGatewayName()]
                    if 'Properties' in api_gateway and 'DefinitionBody' in api_gateway['Properties']:
                        if 'paths' not in api_gateway['Properties']['DefinitionBody']:
                            api_gateway['Properties']['DefinitionBody']['paths'] = {}
                        api_gateway['Properties']['DefinitionBody']['paths'].update(paths)

    def _add_sqs_path_to_api_gateway(self, queue_config: QueueProperty) -> dict:
        """
        Creates API Gateway path configuration for SQS triggers.

        Args:
            queue_config: Queue property with apiTrigger configuration

        Returns:
            Dictionary of API Gateway paths
        """
        api_paths = {}

        if not queue_config.apiTrigger:
            return api_paths

        for route in queue_config.apiTrigger:
            queue_name = self.builder.getQueueName(queue_config.name, 'Q')

            # Build SQS integration URI
            uri = {
                "Fn::Sub": [
                    "arn:aws:apigateway:${AWS::Region}:sqs:path/${AWS::AccountId}/${QueueName}",
                    {"QueueName": {"Fn::GetAtt": [queue_name, "QueueName"]}}
                ]
            }

            # Build request template with message attributes
            request_template = "Action=SendMessage&MessageBody=$input.body"

            # Add headers as message attributes
            if route.headers:
                for i, header in enumerate(route.headers, 1):
                    request_template += (
                        f"&MessageAttribute.{i}.Name={header}"
                        f"&MessageAttribute.{i}.Value.StringValue=$input.params().header.get('{header}')"
                        f"&MessageAttribute.{i}.Value.DataType=String"
                    )

            # Add model type as message attribute
            i = len(route.headers) if route.headers else 0
            if route.modeltype:
                request_template += (
                    f"&MessageAttribute.{i+1}.Name=model"
                    f"&MessageAttribute.{i+1}.Value.StringValue={route.modeltype.value}"
                    f"&MessageAttribute.{i+1}.Value.DataType=String"
                )

            # Build integration configuration
            integration = {
                'x-amazon-apigateway-integration': {
                    'type': 'aws',
                    'httpMethod': 'POST',
                    'uri': uri,
                    'credentials': {"Fn::GetAtt": [self.builder.getApiGatewayRoleName(), "Arn"]},
                    'requestParameters': {
                        'integration.request.header.Content-Type': "'application/x-www-form-urlencoded'"
                    },
                    'requestTemplates': {
                        'application/x-www-form-urlencoded': request_template
                    }
                }
            }

            # Add path with method and integration
            api_paths[route.path] = {
                route.method.lower(): {
                    'responses': {'200': {'description': 'Success'}},
                    **integration
                }
            }

        return api_paths
