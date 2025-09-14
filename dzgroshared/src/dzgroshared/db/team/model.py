# from pydantic import BaseModel
# from pydantic.json_schema import SkipJsonSchema
# from app.HelperModules.Collections.accounts.marketplaces.model import MarketplaceNameId
# from app.HelperModules.Collections.user.model import User

# class TeamMember(User):
#     marketplaceNames: list[MarketplaceNameId] = []

# class TeamMemberList(BaseModel):
#     users: list[TeamMember]
#     token: str|SkipJsonSchema[None] = None

# class AddNewUserRequest(BaseModel):
#     name: str
#     phoneNumber: str
#     email: str
#     groups: list[str]
#     marketplaces: list[str]
    

# class UpdateUserRequest(BaseModel):
#     uid: str
#     groups: list[str]
#     marketplaces: list[str]

# class NewUserResponse(BaseModel):
#     user: TeamMember
#     imageUploaded: bool

# class GroupsAndMarketplaces(BaseModel):
#     groups: list[str]
#     marketplaces: list[MarketplaceNameId]




