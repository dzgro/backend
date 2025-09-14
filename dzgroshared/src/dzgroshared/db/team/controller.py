# from bson import ObjectId
# from app.HelperModules.Collections.accounts.marketplaces.Helper import MarketplaceHelper, MarketplaceNameId
# from app.HelperModules.Collections.user.CognitoApp import User
# from app.HelperModules.Db.DbUtils import DbManager
# from app.HelperModules.Db.models import CollectionType
# from app.HelperModules.Helpers.S3Helper.Storage import S3
# from app.HelperModules.Collections.user.team.model import AddNewUserRequest, GroupsAndMarketplaces, TeamMember, TeamMemberList, UpdateUserRequest
# from app.HelperModules.Collections.user import CognitoManager
# from app.HelperModules.Auth.CommonModels import SuccessResponse

# class TeamHelper:
#     user: User
#     manager: CognitoManager
#     accountManager: MarketplaceHelper
#     db: DbManager

#     def __init__(self, user: User) -> None:
#         self.user = user
#         self.manager = CognitoManager()
#         self.accountManager = MarketplaceHelper(self.user.id)
#         self.db = DbManager(CollectionType.USERS, uid=self.user.id)

#     def getFilter(self, uid: str|list[str]):
#         filter: dict = {"details.parent": self.user.id, "_id": uid}
#         if isinstance(uid, list):  filter['_id'] = {"$in": uid}
#         return filter
    
#     def getMarketplaceIds(self)->list[ObjectId]:
#         res = self.db.findOne({"uid": self.user.id, "parent": self.user.details.parent}, projectionInc=['marketplaces'])
#         if not res: raise ValueError("User does not Exist")
#         return [ObjectId(x) for x in res.get("marketplaces", [])]

#     def getTeamMembersByUids(self, uids: list[str])->list[User]:
#         filter = self.getFilter(uids)
#         data = list(self.db.find(filter))
#         return [User(**x) for x in data]

#     def getTeamMemberDb(self, uid: str)->User:
#         user = self.db.findOne(self.getFilter(uid))
#         if not user: raise ValueError("User not found")
#         return User(**user)

#     def getAllTeamMembersDb(self)->list[User]:
#         data = list(self.db.find({"parent": self.user.details.parent}))
#         return [User(**x) for x in data]

#     def getParentMarketplaces(self)->list[MarketplaceNameId]:
#         return self.accountManager.getAllMarketplaceNames(self.user.id)

#     def getTeamMemberMarketplaces(self, ids: list[str])->list[MarketplaceNameId]:
#         return self.accountManager.getTeamMemberMarketplaces(ids)
    
#     async def uploadImage(self, uid: str, image: bytes, mimeType: str)->SuccessResponse:
#         try:
#             s3 = S3('dzgro-cloudfront')
#             s3.put_object(image, f'users-profile-images/{uid}', mimeType)
#             return SuccessResponse(success=True)
#         except Exception as e:
#             raise ValueError('Image could not be updated')


#     def createTeamMember(self, req: AddNewUserRequest)->TeamMember:
#         try:
#             user = self.manager.create_user(self.user.id, req)
#             return self.getTeamMember(user.id)
#         except Exception as e:
#             raise ValueError('User cannot be added')

#     def updateTeamMember(self, user: UpdateUserRequest)->TeamMember:
#         curr_user = self.manager.get_cognito_user(user.uid)
#         username = curr_user['Username']
#         curr_groups = self.manager.get_user_groups(user.uid)
#         enter_groups = list(filter(lambda x: x not in curr_groups, user.groups))
#         exit_groups = list(filter(lambda x: x not in user.groups, curr_groups))
#         for grp in enter_groups: self.manager.admin_add_user_to_group(username, grp)
#         for grp in exit_groups: self.manager.admin_remove_user_from_group(username, grp)
#         self.db.updateOne(self.getFilter(username), {"marketplaces": user.marketplaces})
#         return self.getTeamMember(user.uid)
    
#     def deleteTeamMember(self, uid: str)->SuccessResponse:
#         uid =  self.manager.delete_user(self.user.id, uid)
#         self.db.deleteOne({"uid": uid, "parent": self.user.id})
#         return SuccessResponse(success=True)
    
#     def getTeamMember(self, uid)->TeamMember:
#         user = self.manager.get_user(uid)
#         # dbUser = self.getTeamMemberDb(uid)
#         member = user.model_dump(exclude_none=True)
#         member['marketplaceNames']=self.getTeamMemberMarketplaces(member.get('marketplaces',[]))
#         return TeamMember(**member)

#     def listTeamMembers(self, token: str|None=None)->TeamMemberList:
#         userList = self.manager.list_sub_users(self.user.id, token)
#         dbUsers = self.getTeamMembersByUids([x.id for x in userList.users])
#         teamMembers: list[TeamMember] = []
#         marketplaces = self.getParentMarketplaces()
#         for user in userList.users:
#             dbUser = next((x.model_dump() for x in dbUsers if x.id==user.id), None)
#             # if dbUser:
#             # userMarketplaces = [x.model_dump() for x in marketplaces if str(x.id) in dbUser.get('marketplaces', [])]
#             member = {**user.model_dump(), 'marketplaceNames': marketplaces}
#             teamMembers.append(TeamMember(**member))
#         return TeamMemberList(users=teamMembers, token=userList.token)
    
    
#     def getGroupsAndMarketplaces(self):
#         allgroups: list[str] = []
#         groups,token = self.manager.list_groups()
#         allgroups = list(filter(lambda x: x!='whatsapp_admin', groups))
#         while token:
#             groups,token = self.manager.list_groups()
#             allgroups.extend(groups)
#         return GroupsAndMarketplaces(groups=allgroups, marketplaces=self.getParentMarketplaces())


    
    


        

    