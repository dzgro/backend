from dzgroshared.db.gstin.model import BusinessDetails, GSTDetail, LinkedGSTs
from dzgroshared.db.enums import GSTStateCode
from fastapi import APIRouter, Request, Depends
from api.Util import RequestHelper
from dzgroshared.db.model import PyObjectId, SuccessResponse
router = APIRouter(prefix="/gst", tags=["GST"])

async def db(request: Request):
    return (await RequestHelper(request).client).db.gstin


@router.get("/list", response_model=LinkedGSTs, response_model_exclude_none=True, response_model_by_alias=False)
async def listGST(request: Request):
    return await (await db(request)).listGSTs()

@router.get("/states", response_model=list[GSTStateCode], response_model_exclude_none=True, response_model_by_alias=False)
async def getStates(request: Request):
    return GSTStateCode.values()

@router.get("/{id}", response_model=GSTDetail, response_model_exclude_none=True, response_model_by_alias=False)
async def getGST(request: Request, id: PyObjectId):
    return await (await db(request)).getGST(id)

@router.post("/", response_model=GSTDetail, response_model_exclude_none=True, response_model_by_alias=False)
async def addGST(request: Request, details: BusinessDetails):
    return await (await db(request)).addGST(details)

@router.put("/{id}", response_model=GSTDetail, response_model_exclude_none=True, response_model_by_alias=False)
async def updatesGST(request: Request, id: PyObjectId, details: BusinessDetails):
    return await (await db(request)).updateGST(id, details)

@router.delete("/{id}", response_model=SuccessResponse, response_model_exclude_none=True, response_model_by_alias=False)
async def deleteGST(request: Request, id: PyObjectId):
    return await (await db(request)).deleteGST(id)