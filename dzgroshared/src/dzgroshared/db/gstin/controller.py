from bson import ObjectId
from dzgroshared.db.gstin.model import BusinessDetails, LinkedGsts, GstDetail
from dzgroshared.db.enums import CollectionType
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient
from dzgroshared.db.model import PyObjectId, SuccessResponse

class GSTHelper:
    client: DzgroSharedClient
    db:DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.client = client
        self.db = DbManager(client.db.database.get_collection(CollectionType.GSTIN.value), uid=self.client.uid)

    async def listGSTs(self):
        data = await self.db.find({"uid": self.client.uid})
        return LinkedGsts.model_validate({"data": data})

    async def getGST(self, id: PyObjectId):
        data = await self.db.findOne({"_id": id, "uid": self.client.uid})
        return GstDetail.model_validate({"data": data})
    
    async def addGST(self, req: BusinessDetails):
        data = {**req.model_dump(mode="json"), "uid": self.client.uid}
        id = await self.db.insertOne(data)
        return self.getGST(PyObjectId(id))
    
    async def updateGST(self, id: PyObjectId, req: BusinessDetails):
        await self.db.updateOne({"_id": id}, setDict=req.model_dump(mode="json"))
        return self.getGST(id)
        
    async def deleteGST(self, id: PyObjectId):
        linkedMarketplace = await self.client.db.marketplaces.db.count({"gstin": id})
        if linkedMarketplace>0: raise ValueError("GSTIN is linked to a marketplace. Unlink before deleting.")
        count = await self.db.deleteOne({"_id": id})
        return SuccessResponse(success=count>0)
    
    