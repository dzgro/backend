from dzgroshared.db.DbUtils import DbManager
from dzgroshared.models.enums import CollectionType
from dzgroshared.client import DzgroSharedClient

class CalculationKeysHelper:
    db: DbManager

    def __init__(self, client: DzgroSharedClient) -> None:
        self.db = DbManager(client.db.database.get_collection(CollectionType.ANALYTICS_CALCULATION.value))

    async def getGroups(self):
        setDict = self.db.pp.set({ 'items': { '$map': { 'input': { '$filter': { 'input': '$items', 'as': 'f', 'cond': { "$ne": [{'$ifNull': [ '$$f.querygroup', None ]},None] } } }, 'as': 'i', 'in': { 'label': '$$i.label', 'value': '$$i.value' } } } })
        sort = self.db.pp.sort({"index": 1})
        project = self.db.pp.project(['label','items'],["_id"])
        pipeline = [setDict, sort, project]
        return await self.db.aggregate(pipeline)
    
    async def getAdColumns(self):
        matchStage = self.db.pp.match({"value": "ad"})
        project = self.db.pp.project(['items'],["_id"])
        unwind = self.db.pp.unwind("items")
        replaceWith = self.db.pp.replaceWith("$items")
        projectkv = self.db.pp.project(['label',"value"])
        data = await self.db.aggregate([matchStage, project, unwind, replaceWith, projectkv])
        for item in data:
            label: str = item['label']
            if label.startswith('Ad '): item['label'] = label[3:]
            if '(' in label: item['label'] = label[label.index('(')+1:label.index(')')]
        return data

    





    