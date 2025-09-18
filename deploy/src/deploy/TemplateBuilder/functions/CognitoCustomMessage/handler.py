def handler(event, context):
    trigger = event["triggerSource"]

    if trigger == "CustomMessage_SignUp":
        event["response"]["emailSubject"] = "Your Dzgro verification code"
        event["response"]["emailMessage"] = (
            f"Hello {event['userName']},\n\n"
            f"Your verification code is: {event['request']['codeParameter']}\n\n"
            f"Enter this code in the app to complete signup."
        )

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
