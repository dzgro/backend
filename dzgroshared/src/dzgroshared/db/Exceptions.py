from dzgroshared.models.model import CustomError


INVALID_CREDENTIALS = CustomError({"error": "Not Authenticated"})
INVALID_USER = CustomError({"error": "User not found"})
UNAUTHORISED = CustomError({"error": "User not authorised for this operation"})
INVALID_MARKETPLACE = CustomError({"error": "Invalid Marketplace"})
MISSING_MARKETPLACE = CustomError({"error": "Marketplace not found"})
NO_MARKETPLACES = CustomError({"error": "User Not Onboarded"})
MISSING_SPAPI_ACCOUNT = CustomError({"error": "SPAPI Account does not exist"})
MISSING_ADVERISING_ACCOUNT = CustomError({"error": "Advertising Account does not exist"})
MISSING_SELLER_TOKEN = CustomError({"error": "Seller Token does not exist"})
UNAUTHORISED_MARKETPLACE = CustomError({"error": "Marketplace not authorised"})
INVALID_COUNTRY_CODE = CustomError({"error": "Invalid Country Code"})
UNEXPECTED_ERROR = CustomError({"error": "Some Error Occurred"})
