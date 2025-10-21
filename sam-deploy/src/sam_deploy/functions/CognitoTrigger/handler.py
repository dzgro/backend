import os
import json
import boto3
from pymongo import MongoClient
from pymongo.collection import Collection
client=None

def getMongoClient()->Collection|None:
    global client
    if client: return client
    from dzgro_secrets.client import SecretManager
    secrets = SecretManager()
    return MongoClient(secrets.MONGO_DB_CONNECT_URI)[secrets.DB_NAME]['users']
    
def checkSignUp(event):
    client = boto3.client('cognito-idp')
    user_pool_id = event['userPoolId']
    email = event['request']['userAttributes'].get('email')
    if not email:
        print("No email in event — skipping cleanup.")
        return event
    try:
        response = client.list_users( UserPoolId=user_pool_id, Filter=f'email = "{email}"' )
        for user in response.get('Users', []):
            if user.get('UserStatus') == 'UNCONFIRMED':
                username = user['Username']
                client.admin_delete_user( UserPoolId=user_pool_id, Username=username )
                print(f"Deleted unconfirmed user {username} for email {email}")
    except Exception as e:
        print(f"Error checking/deleting existing user: {str(e)}")
    return event

def confirmSignUp(event):
    client = getMongoClient()
    username = event.get("userName",None)
    if client is None or username is None: return event
    attrs = event["request"]["userAttributes"]
    user_doc = { "_id": username, "name": attrs.get("name"), "email": attrs.get("email"), "phone_number": attrs.get("phone_number"), "status": "Pending Onboarding" }
    try:
        client.update_one( {"_id": username}, {"$setOnInsert": user_doc}, upsert=True )
        print(f"✅ User {username} inserted")
    except Exception as e:
        print(f"❌ DB insert failed: {e}")
    return event
        
def generateToken(event):
    client = getMongoClient()
    username = event.get("userName",None)
    if client is None or username is None: return event
    status = "unknown"
    doc = client.find_one({"_id": username}, {"status": 1})
    if doc and "status" in doc:
        status = doc["status"]
    # print(f"🔑 status: {status}")
    event['response'] = { 'claimsAndScopeOverrideDetails': { 'idTokenGeneration': { 'claimsToAddOrOverride': { 'status': status } }, 'accessTokenGeneration': { 'claimsToAddOrOverride': { 'status': status }, 'scopesToAdd': ['dzgro/read'] } } }
    return event

def sendMessage(event, trigger):
    
    def getEmailMessage(message):
        return f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f7f9fc; padding: 20px;">
                <table width="100%" cellspacing="0" cellpadding="0" style="max-width: 500px; margin: auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                <tr>
                    <td style="padding: 30px; text-align: center;">
                    <h2 style="color: #2F855A; margin-bottom: 20px;">Welcome, {event['request']['userAttributes']['name'].title()}!</h2>
                    <p style="font-size: 16px; color: #333333; margin-bottom: 25px;">
                        {message}
                    </p>
                    <div style="font-size: 32px; font-weight: bold; color: #ffffff; background-color: #2F855A; padding: 15px 25px; border-radius: 6px; display: inline-block; letter-spacing: 3px;">
                        {event['request']['codeParameter']}
                    </div>
                    <p style="margin-top: 30px; font-size: 14px; color: #555555;">
                        If you didn’t request this code, you can safely ignore this email.
                    </p>
                    </td>
                </tr>
                </table>
                <p style="text-align: center; font-size: 12px; color: #999999; margin-top: 20px;">
                © 2023 Dzgro Technologies. All rights reserved.
                </p>
            </body>
            </html>
        """
    if trigger == "CustomMessage_SignUp":
        event["response"]["emailSubject"] = "🔐 Your Dzgro verification code"
        event["response"]["emailMessage"] = getEmailMessage("Use the verification code below to complete your signup:")

    elif trigger == "CustomMessage_ForgotPassword":
        event["response"]["emailSubject"] = "🔐 Reset your Dzgro password"
        event["response"]["emailMessage"] = getEmailMessage("Use this code to reset your password:")

    elif trigger == "CustomMessage_ResendCode":
        event["response"]["emailSubject"] = "🔐 Your New Dzgro verification code"
        event["response"]["emailMessage"] = getEmailMessage(f"Here is your code again:")
    return event
    

def handler(event, context):
    try:
        print("Event:", json.dumps(event))
        trigger = event.get("triggerSource", "")
        if trigger == "PreSignUp_SignUp":
            return checkSignUp(event)
        elif trigger in ["CustomMessage_SignUp", "CustomMessage_ForgotPassword", "CustomMessage_ResendCode"]:
            return sendMessage(event, trigger)
        else:
            if event["triggerSource"] == "PostConfirmation_ConfirmSignUp": return confirmSignUp(event)
            elif event["triggerSource"] == "TokenGeneration_HostedAuth": return generateToken(event)
    except Exception as e:
        print(f"Error in Cognito trigger handler: {e}")
    return event
