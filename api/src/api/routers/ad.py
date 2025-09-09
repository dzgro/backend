import asyncio
from bson import ObjectId
from pydantic.json_schema import SkipJsonSchema
from fastapi import APIRouter, BackgroundTasks, Body, Path, Request
from dzgroshared.models.model import Paginator, SuccessResponse
from dzgroshared.models.collections.adv_ad_group_mapping import AdGroupMapping
from dzgroshared.models.enums import AdAssetType, AdProduct
from dzgroshared.models.collections.adv_assets import AdBreadcrumb, ListAdAssetRequest, ListAdAssetRequestParams, AdAssetResponse
from dzgroshared.models.extras.ad_structure import AdGroupCompliance,ViolatingAdGroupAd, ViolatingAdGroupMatchType, ViolatingAdGroupTarget, AdGroupOptimizationRequest, AdGroupOptimizationResponse
from dzgroshared.db.extras.rule_executor import AdRuleExecutor
from dzgroshared.models.collections.adv_rule_runs import AdRuleRun, AdRuleRunRequest, AdRuleRunResultParams, AdRuleWithRunDetails, AdRuleRunResult, RuleAvailableFilters
from dzgroshared.models.collections.adv_rules import AdRuleAssetTypeWithAdProduct, AdRuleSummary, AdCriteriaParams, CreateAdRuleRequest, AdRule, SimplifyAdRuleRequest
router = APIRouter(prefix="/ad", tags=["Advertisement"])
from api.Util import RequestHelper


async def getAdvertisementHelper(request: Request):
    return (await RequestHelper(request).client).db.adv_assets

async def getAdRuleUtility(request: Request):
    return (await RequestHelper(request).client).db.ad_rule_utility

async def getDashboardHelper(request: Request):
    return (await RequestHelper(request).client).db.analytics

async def getAdRuleRunUtility(request: Request):
    return (await RequestHelper(request).client).db.ad_rule_run_utility

async def getAdRuleRunResultsUtility(request: Request):
    return (await RequestHelper(request).client).db.ad_rule_run_results

async def getAdGroupMappingHelper(request: Request):
    return (await RequestHelper(request).client).db.ad_group_mapping

async def getAdStructureHelper(request: Request):
    return (await RequestHelper(request).client).db.ad_structure



@router.post("/list", response_model=AdAssetResponse, response_model_exclude_none=True)
async def listAdAssets(request: Request, body: ListAdAssetRequest):
    return (await getAdvertisementHelper(request)).listAssets(body)

@router.get("/listRequestParams", response_model=ListAdAssetRequestParams, response_model_exclude_none=True)
async def getTableColumns(request: Request):
    return (await getDashboardHelper(request)).getPerformanceParams()

@router.post("/rule", response_model=AdRule, response_model_exclude_none=True, response_model_by_alias=False)
async def createRule(request: Request, req: CreateAdRuleRequest):
    return (await getAdRuleUtility(request)).addRule(req)

@router.post("/rule/template", response_model=dict, response_model_exclude_none=True, response_model_by_alias=False)
async def createRuleTemplate(request: Request, req: CreateAdRuleRequest):
    return (await getAdRuleUtility(request)).createTemplate(req)

@router.get("/rules/params", response_model=list[AdRuleAssetTypeWithAdProduct], response_model_exclude_none=True)
async def getNewRuleFormParams(request: Request):
    return (await getAdRuleUtility(request)).getRuleParams()

@router.put("/rule/{ruleid}", response_model=AdRule, response_model_exclude_none=True, response_model_by_alias=False)
async def updateRuleBasicDetails(request: Request,ruleid:str, req: CreateAdRuleRequest):
    return (await getAdRuleUtility(request)).updateRule(ruleid,req)

@router.delete("/rule/{id}", response_model=SuccessResponse, response_model_exclude_none=True)
async def deleteRule(request: Request, id: str):
    return (await getAdRuleUtility(request)).deleteRule(id)

@router.get("/rule/{id}", response_model=AdRule, response_model_exclude_none=True, response_model_by_alias=False)
async def getRule(request: Request, id:str):
    return (await getAdRuleUtility(request)).getRuleById(id)

@router.post("/rules", response_model=list[AdRule], response_model_exclude_none=True, response_model_by_alias=False)
async def listRules(request: Request, paginator: Paginator, assettype: AdAssetType|SkipJsonSchema[None] =None):
    return (await getAdRuleUtility(request)).getRules(paginator,assettype)

@router.get("/rules/templates", response_model=list[AdRule], response_model_exclude_none=True, response_model_by_alias=False)
async def listRuleTemplates(request: Request):
    return (await getAdRuleUtility(request)).getRuleTemplates()

@router.post("/rules/criterias/simplify", response_model=AdRuleSummary, response_model_exclude_none=True)
async def simplifyCriterias(request: Request, req: SimplifyAdRuleRequest):
    return (await getAdRuleUtility(request)).summariseAdRule(req)

@router.get("/rules/template/{templateid}", response_model=AdRule, response_model_exclude_none=True, response_model_by_alias=False)
async def getTemplateById(request: Request, templateid: str):
    return (await getAdRuleUtility(request)).getTemplateById(templateid)

@router.get("/rules/criterias", response_model=AdCriteriaParams, response_model_exclude_none=True)
async def getRuleCriterias(request: Request, assettype: AdAssetType, adproduct: AdProduct):
    return (await getAdRuleUtility(request)).getCriteriaGroups(assettype, adproduct)

@router.get("/detail/{runId}", response_model=AdRuleWithRunDetails, response_model_exclude_none=True, response_model_by_alias=False)
async def getRuleAndRunDetails(request: Request, runId: str):
    return (await getAdRuleRunUtility(request)).getRunById(runId)

@router.post("/list/{ruleId}", response_model=list[AdRuleRun], response_model_exclude_none=True, response_model_by_alias=False)
async def getRuleRunByIds(request: Request, runIds: list[str], ruleId: str):
    return (await getAdRuleRunUtility(request)).getRunsByIds(ruleId, runIds)

@router.post("/runs/{ruleId}", response_model=list[AdRuleRun], response_model_exclude_none=True, response_model_by_alias=False)
async def listRunsByRuleId(request: Request, paginator: Paginator, ruleId: str):
    return (await getAdRuleRunUtility(request)).getRuns(ruleId, paginator)

@router.post("/run/results/{runId}", response_model=list[AdRuleRunResult], response_model_exclude_none=True, response_model_by_alias=False)
async def listRuleRunResults(request: Request, paginator: Paginator, runId: str):
    return (await getAdRuleRunUtility(request)).getRuleRunResults(runId, paginator)

@router.get("/run/results/count/{runId}", response_model=AdRuleRunResultParams, response_model_exclude_none=True, response_model_by_alias=False)
async def getRuleRunCountWithColumns(request: Request, runId: str):
    return (await getAdRuleRunUtility(request)).getRuleRunCountWithColumns(runId)

@router.get("/rule-filters/{adProduct}/{assettype}", response_model=list[RuleAvailableFilters], response_model_exclude_none=True, response_model_by_alias=False)
async def getRuleFilterForRun(request: Request, adProduct:AdProduct, assettype: AdAssetType):
    return (await getAdvertisementHelper(request)).getFiltersForAdRuleRun(adProduct, assettype)

@router.post("/run-rule", response_model=AdRuleRun, response_model_exclude_none=True, response_model_by_alias=False)
async def runAdRule(request: Request, tasks: BackgroundTasks, req: AdRuleRunRequest):
    utility = (await getAdRuleRunUtility(request))
    run = await utility.runRule(req)
    # tasks.add_task(AdRuleExecutor,marketplace=utility.marketplace, runid=str(run.id))
    return run

@router.post("/execute/{ruleId}/{runId}", response_model=SuccessResponse, response_model_exclude_none=True)
async def executeRun(request: Request, discardIds: list[str], ruleId: str, runId: str):
    await (await getAdRuleRunUtility(request)).execute(ruleId, runId, discardIds)
    SuccessResponse(success=True)

@router.get("/structure/violations/adgroups", response_model=list[AdGroupCompliance], response_model_exclude_none=True)
async def getViolatingAdGroupsWithMultipleAsins(request: Request):
    return (await getAdStructureHelper(request)).getAdGroupWithStructureViolations()

@router.get("/structure/violations/adgroups/{adgroupid}", response_model=AdGroupCompliance, response_model_exclude_none=True)
async def getAdGroupViolation(request: Request, adgroupid: str):
    return (await getAdStructureHelper(request)).getAdGroupViolation(adgroupid)

@router.post("/structure/{adgroup}/ads", response_model=list[ViolatingAdGroupAd], response_model_exclude_none=True)
async def getAdByViolatingAdGroupsWithMultipleAsins(request: Request, adgroup:str):
    return (await getAdStructureHelper(request)).getMultipleAsinViolationByAdgroupId(adgroup)

@router.post("/structure/{adgroup}/match-types", response_model=list[ViolatingAdGroupMatchType], response_model_exclude_none=True)
async def getMatchTypesForAdGroup(request: Request, adgroup:str):
    return (await getAdStructureHelper(request)).getMatchTypesForAdGroup(adgroup)

@router.post("/structure/{adgroup}/targets", response_model=list[ViolatingAdGroupTarget], response_model_exclude_none=True)
async def getTargetsForAdGroup(request: Request, adgroup:str, matchtype:str|SkipJsonSchema[None]=None):
    return (await getAdStructureHelper(request)).getTargetsForAdGroup(adgroup, matchtype)

# @router.post("/mapping/list", response_model=list[AdGroupMapping], response_model_exclude_none=True)
# async def getMapping(request: Request, paginator: Paginator):
#     return await Ad(request).getAdGroupMappingHelper().listMappings(paginator)

# @router.post("/mapping/create")
# async def createMapping(request: Request, body: AdGroupMapping):
#     return await Ad(request).getAdGroupMappingHelper().createMapping(body)
#     return utility

# @router.post("/structure/optimize", response_model=AdGroupOptimizationResponse, response_model_exclude_none=True)
# async def optimizeAdGroup(request: Request, body: AdGroupOptimizationRequest):
#     return await Ad(request).getAdGroupOptimiserHelper().optimiseAdGroup(body)
    

    