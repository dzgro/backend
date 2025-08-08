from models.model import CustomError

INVALID_CREDENTIALS = ValueError("Not Authenticated")
INVALID_USER = ValueError("User not found")
UNAUTHORISED = ValueError("User not authorised for this operation")
INVALID_MARKETPLACE = ValueError("Invalid Marketplace")
MISSING_MARKETPLACE = ValueError("Marketplace not found")
MISSING_SPAPI_ACCOUNT = ValueError("SPAPI Account does not exist")
MISSING_ADVERISING_ACCOUNT = ValueError("Advertising Account does not exist")
MISSING_SELLER_TOKEN = ValueError("Seller Token does not exist")
UNAUTHORISED_MARKETPLACE = ValueError("Marketplace not authorised")
INVALID_COUNTRY_CODE = ValueError("Invalid Country Code")
UNEXPECTED_ERROR = CustomError({"error": "Some Error Occurred"})
