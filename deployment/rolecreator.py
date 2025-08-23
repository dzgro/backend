
import boto3
from botocore.exceptions import ClientError
import json
iam = boto3.client('iam')

class RoleCreator:

    def __init__(self) -> None:
        pass

    
    def create_api_gateway_role(self)->str:
        """
        Creates IAM role DzgroAPIGatewayRole with required policies and returns the role ARN.
        """
        iam = boto3.client('iam')
        role_name = 'DzgroAPIGatewayRole'
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "apigateway.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        policies = [
            'arn:aws:iam::aws:policy/AWSLambdaBasicExecutionRole',
            'arn:aws:iam::aws:policy/AmazonSQSFullAccess'
        ]
        try:
            # Check if role exists
            response = iam.get_role(RoleName=role_name)
            print(f"Role {role_name} already exists.")
            return response['Role']['Arn']
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                try:
                    print(f"Creating role: {role_name}")
                    response = iam.create_role(
                        RoleName=role_name,
                        AssumeRolePolicyDocument=json.dumps(assume_role_policy)
                    )
                    for policy_arn in policies:
                        iam.attach_role_policy(
                            RoleName=role_name,
                            PolicyArn=policy_arn
                        )
                    print(f"Role {role_name} created and policies attached.")
                    return response['Role']['Arn']
                except ClientError as ce:
                    raise ValueError(f"Error creating role {role_name}: {ce}")
            else:
                raise ValueError(f"Error checking role {role_name}: {e}")



    def create_lambda_role(self)->str:
        role_name = 'DzgroLambdaRole'
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        policies = [
            'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
            'arn:aws:iam::aws:policy/AmazonSQSFullAccess',
            'arn:aws:iam::aws:policy/AmazonS3FullAccess'
        ]
        try:
            # Check if role exists
            response = iam.get_role(RoleName=role_name)
            print(f"Role {role_name} already exists.")
            return response['Role']['Arn']
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                try:
                    print(f"Creating role: {role_name}")
                    response = iam.create_role(
                        RoleName=role_name,
                        AssumeRolePolicyDocument=json.dumps(assume_role_policy)
                    )
                    for policy_arn in policies:
                        iam.attach_role_policy(
                            RoleName=role_name,
                            PolicyArn=policy_arn
                        )
                    print(f"Role {role_name} created and policies attached.")
                    return response['Role']['Arn']
                except ClientError as ce:
                    raise ValueError(f"Error creating role {role_name}: {ce}")
            else:
                raise ValueError(f"Error checking role {role_name}: {e}")
            

    