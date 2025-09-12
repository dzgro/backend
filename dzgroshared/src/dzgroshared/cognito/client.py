
from mypy_boto3_cognito_idp import CognitoIdentityProviderClient
from typing import cast as Cast

class CognitoManager:
    client: CognitoIdentityProviderClient
    COGNITO_APP_CLIENT_ID: str
    COGNITO_USER_POOL_ID: str

    def __init__(self, COGNITO_APP_CLIENT_ID: str, COGNITO_USER_POOL_ID: str) -> None:
        import boto3
        from botocore.config import Config
        self.client = Cast(CognitoIdentityProviderClient, boto3.client('cognito-idp', config=Config(region_name = 'ap-south-1')))
        self.COGNITO_APP_CLIENT_ID = COGNITO_APP_CLIENT_ID
        self.COGNITO_USER_POOL_ID = COGNITO_USER_POOL_ID

    def getAccessToken(self, username: str, password: str):
        try:
            response = self.client.initiate_auth(
                ClientId=self.COGNITO_APP_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            return response['AuthenticationResult'].get('AccessToken', None)
        except Exception as e:
            raise ValueError(e.args[0])


    def signout(self, token:str):
        try:
            self.client.global_sign_out(AccessToken=token)
        except Exception as e:
            raise ValueError(e.args[0])
        
    def get_attribute_value_by_key(self, key: str, user_attributes: list):
        return next((x['Value'] for x in user_attributes if x['Name']==key and 'Value' in x), None)
    
    def get_user_details_by_attributes(self, user_attributes: list):
        name = self.get_attribute_value_by_key('name',user_attributes)
        phoneNumber = self.get_attribute_value_by_key('phone_number',user_attributes)
        email = self.get_attribute_value_by_key('email',user_attributes)
        parent = self.get_attribute_value_by_key('preferred_username', user_attributes)
        return {"name": name, "phoneNumber": phoneNumber, "email": email, "parent": parent}
    
    def delete_user(self, uid: str, userUid: str)->str:
        response = self.get_cognito_user(userUid)
        parent_uid = self.get_attribute_value_by_key('preferred_username',response['UserAttributes'])
        if parent_uid!=uid: raise ValueError("User cannot be deleted")
        self.client.admin_delete_user(
            UserPoolId=self.COGNITO_USER_POOL_ID,
            Username=userUid
        )
        return response['Username']
    
    def admin_add_user_to_group(self, username: str, group: str):
        self.client.admin_add_user_to_group(UserPoolId=self.COGNITO_USER_POOL_ID, Username=username, GroupName=group)
    
    def admin_remove_user_from_group(self, username: str, group: str):
        self.client.admin_remove_user_from_group(UserPoolId=self.COGNITO_USER_POOL_ID, Username=username, GroupName=group)
    
    def list_groups(self, token: str|None=None)->tuple[list[str], str|None]:
        if not token: result = self.client.list_groups(UserPoolId=self.COGNITO_USER_POOL_ID,Limit=10)
        else: result = self.client.list_groups(UserPoolId=self.COGNITO_USER_POOL_ID,Limit=10, NextToken=token)
        groups: list[str] = []
        for x in result.get('Groups', []):
            name = x.get('GroupName', None)
            if name: groups.append(name)
        return groups, result.get('NextToken',None)
    
    def get_cognito_user(self, uid: str):
        return self.client.admin_get_user(
            UserPoolId=self.COGNITO_USER_POOL_ID,
            Username=uid
        )
    
    async def get_user(self, sub: str)->tuple[str, dict]:
        user = self.get_cognito_user(sub)
        return await self.get_user_by_attributes(user)
        
    
    async def get_user_by_attributes(self, user)->tuple[str, dict]:
        username, attributes, status = (user['Username'], user.get('UserAttributes', user.get('Attributes', [])), user['UserStatus'])
        details: dict[str, str|None] = self.get_user_details_by_attributes(attributes)
        name = details.get("name", None)
        email = details.get("email", None)
        phoneNumber = details.get("phoneNumber", None)
        parent = details.get("parent", None) or username
        if not name or not  email or not phoneNumber: raise ValueError("Invalid User")
        userDict = {
            "name": name, "email": email, "phoneNumber": phoneNumber, "username": username, "status": status, "groups": self.get_user_groups(username), "parent": parent
        }
        return username, userDict

    async def get_user_groups(self, sub: str)->list[str]:
        groups: list[str] = []
        try:
            response = self.client.admin_list_groups_for_user(
                Username=sub,
                UserPoolId=self.COGNITO_USER_POOL_ID,
                Limit=50
            )
            for group in response['Groups']:
                name = group.get("GroupName", None)
                if name: groups.append(name)
            return groups
        except Exception as e:
            return groups
