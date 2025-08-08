from pydantic import BaseModel, Field, RootModel
from pydantic.json_schema import SkipJsonSchema
from typing import List, Optional, Union

class AlternateId(BaseModel):
    profileId: Optional[int] = Field(None, description="Profile ID for the alternate ID")
    entityId: Optional[str] = Field(None, description="Entity ID for the alternate ID")
    countryCode: str = Field(..., description="Country code for the alternate ID")

class AdsAccount(BaseModel):
    adsAccountId: str = Field(..., description="The unique identifier for the ads account")
    accountName: str = Field(..., description="The name of the ads account")
    status: str = Field(..., description="Status of the ads account")
    countryCodes: List[str] = Field(..., description="List of country codes associated with the account")
    alternateIds: List[AlternateId] = Field(..., description="Alternate IDs for the ads account")

class AdsAccountsListResponse(BaseModel):
    adsAccounts: List[AdsAccount] = Field(..., description="List of ads accounts")
    nextToken: Optional[str] = Field(None, description="Token for the next page of results, if available")


class AdsAccountsListRequest(BaseModel):
    maxResults: int = Field(default=100, description="Maximum number of ads accounts to return", ge=1, le=100)
    nextToken: str|SkipJsonSchema[None] = Field(default=None, description="Token for the next page of results, if available")
