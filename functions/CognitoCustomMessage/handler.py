def handler(event, context):
    trigger = event["triggerSource"]

    if trigger == "CustomMessage_SignUp":
        event["response"]["emailSubject"] = "🔐 Your Dzgro Verification Code"
        event["response"]["emailMessage"] = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f7f9fc; padding: 20px;">
            <table width="100%" cellspacing="0" cellpadding="0" style="max-width: 500px; margin: auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
            <tr>
                <td style="padding: 30px; text-align: center;">
                <h2 style="color: #2F855A; margin-bottom: 20px;">Welcome, {event['request']['userAttributes']['name'].title()}!</h2>
                <p style="font-size: 16px; color: #333333; margin-bottom: 25px;">
                    Use the verification code below to complete your signup:
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
            © 2025 Dzgro Technologies. All rights reserved.
            </p>
        </body>
        </html>
        """

    elif trigger == "CustomMessage_ForgotPassword":
        event["response"]["emailSubject"] = "Reset your Dzgro password"
        event["response"]["emailMessage"] = (
            f"Use this code to reset your password: {event['request']['codeParameter']}"
        )

    elif trigger == "CustomMessage_ResendCode":
        event["response"]["emailSubject"] = "Your Dzgro verification code (resend)"
        event["response"]["emailMessage"] = (
            f"Here is your code again: {event['request']['codeParameter']}"
        )

    return event
