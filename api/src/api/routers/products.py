from api.decorators import cache_control, enforce_response_model
from fastapi import APIRouter, Request
router = APIRouter(prefix="/products", tags=["Products"])
from dzgroshared.db.products.model import AsinView, Product
from api.Util import RequestHelper


async def db(request: Request):
    return (await RequestHelper(request).client).db.products

@router.get("/sku/{sku}", response_model=Product, response_model_exclude_none=True)
async def getSku(request: Request, sku:str):
    return await (await db(request)).getSku(sku)

@router.get("/parentsku/{sku}", response_model=Product, response_model_exclude_none=True)
async def getParentSku(request: Request, sku:str):
    return await (await db(request)).getParentSku(sku)

@router.post("/skus", response_model=list[Product], response_model_exclude_none=True)
async def getSkus(request: Request, skus:list[str]):
    return await (await db(request)).getSkus(skus)


@router.get("/asin/{asin}", response_model=AsinView, response_model_exclude_none=True)
@cache_control()
@enforce_response_model(AsinView)
async def getAsin(request: Request, asin:str):
    return await (await db(request)).getAsin(asin)

@router.post("/asin", response_model=list[Product], response_model_exclude_none=True)
async def getAsins(request: Request, asins:list[str]):
    return await (await db(request)).getAsins(asins)

# @router.get("/categories/count/{queryId}", response_model=list[CategoryCount], response_model_exclude_none=True)
# def getCategoriesWithCount(request: Request, queryId:str):
#     user, marketplace = auth.validate(request)
#     return QueryResultsHelper(marketplace, user.id).getCategoryCounts(queryId)

# @router.get("/filterMetrics", response_model=ProductPerformanceFilterMetric)
# def getFilterMetrics(request: Request):
#     user, marketplace = auth.validate(request)
#     return QueryResultsHelper(marketplace, user.id).getFilterMetrics()

# @router.post("/performance", response_model=list[ListingResponse], response_model_exclude_none=True)
# def getProductsByCategory(request: Request, body: ListingRequest):
#     user, marketplace = auth.validate(request)
#     return QueryResultsHelper(marketplace, user.id).getAsinsByCategoryAndkey(body)

# @router.post("/query/results", response_model=list[QueryResults], response_model_exclude_none=True)
# def getQueryResults(request: Request, body: AsinQueryRequest):
#     user = DzgroRequest(request)
#     return []
    # return QueryResultsHelper(user.marketplaceId, user.user.id).getPerformanceResults(body)

