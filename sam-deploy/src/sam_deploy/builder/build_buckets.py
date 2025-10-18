from sam_deploy.config.mapping import S3Property, ENVIRONMENT, Region
from sam_deploy.builder.template_builder import TemplateBuilder


class BucketBuilder:
    builder: TemplateBuilder

    def __init__(self, builder: TemplateBuilder) -> None:
        self.builder = builder

    def build_bucket(self, bucket_config: S3Property, env: ENVIRONMENT) -> dict[str, dict]:
        """
        Creates S3 bucket resource with lifecycle rules and CORS configuration.

        Args:
            bucket_config: S3 property containing name, roles, lifecycle, CORS, etc.
            env: Environment (DEV, STAGING, PROD, LOCAL)

        Returns:
            Dictionary of CloudFormation resources (S3 bucket)
        """
        resources = {}

        # Generate bucket names
        resource_name = self.builder.getBucketResourceName(bucket_config.name)
        bucket_name = self.builder.getBucketName(bucket_config.name)

        # Build bucket properties
        properties = {
            'BucketName': bucket_name,
            'Tags': self.builder.getListTag()
        }

        # Add lifecycle configuration if specified
        if bucket_config.lifeCycleConfiguration:
            properties['LifecycleConfiguration'] = bucket_config.lifeCycleConfiguration.model_dump(mode="json")

        # Add CORS configuration if specified
        if bucket_config.cors:
            # Determine allowed origins based on environment
            if env == ENVIRONMENT.LOCAL:
                origins = ["https://localhost:4200"]
            else:
                origins = [self.builder.envDomain()]

            properties['CorsConfiguration'] = {
                "CorsRules": [
                    {
                        "AllowedOrigins": origins,
                        "AllowedMethods": [method.value for method in bucket_config.cors.methods],
                        "AllowedHeaders": ["*"],
                        "MaxAge": 3000
                    }
                ]
            }

        # Create bucket resource
        resources[resource_name] = {
            'Type': 'AWS::S3::Bucket',
            'Properties': properties
        }

        return resources

    def build_s3_trigger(
        self,
        bucket_config: S3Property,
        function_name: str
    ) -> dict:
        """
        Creates S3 event notification configuration to trigger Lambda function.
        This is added to the Lambda function's Events property.

        Args:
            bucket_config: S3 property containing trigger configuration
            function_name: Lambda function name to attach to bucket

        Returns:
            Dictionary with S3 event configuration, or empty dict if no trigger
        """
        if not bucket_config.trigger:
            return {}

        resource_name = self.builder.getBucketResourceName(bucket_config.name)

        # Build S3 event configuration
        event_config = {
            "Bucket": {"Ref": resource_name},
            "Events": bucket_config.trigger.eventName
        }

        # Add filter rules if specified
        if bucket_config.trigger.filter:
            event_config["Filter"] = bucket_config.trigger.filter

        return {
            "S3UploadEvent": {
                "Type": "S3",
                "Properties": event_config
            }
        }

    def execute(
        self,
        buckets: list[S3Property],
        region: Region
    ) -> dict[str, dict]:
        """
        Builds all S3 buckets for all 4 environments (DEV, STAGING, PROD, LOCAL).
        Configures lifecycle rules, CORS, and S3 trigger events where applicable.

        Args:
            buckets: List of S3 bucket configurations
            region: AWS region

        Returns:
            Dictionary of S3 trigger events (to be added to Lambda function Events)
        """
        s3_events = {}

        for bucket_config in buckets:
            # Build bucket resources (bucket with lifecycle and CORS)
            bucket_resources = self.build_bucket(bucket_config, self.builder.env)
            self.builder.resources.update(bucket_resources)

            # Build S3 trigger events if configured
            if bucket_config.trigger:
                trigger_event = self.build_s3_trigger(bucket_config, "")
                if trigger_event:
                    # Store trigger events to be added to Lambda function later
                    # Key is bucket name, value is the event configuration
                    s3_events[bucket_config.name.value] = trigger_event

        return s3_events
