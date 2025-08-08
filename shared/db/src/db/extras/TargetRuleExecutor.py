from datetime import datetime, timedelta
import json, time
from app.HelperModules.Db.models import CollectionType
from bson import ObjectId
from app.HelperModules.AmazonApi.model import AmazonApiResponse
from app.HelperModules.Auth.CommonModels import Paginator
from app.HelperModules.Collections.dzgro.adv.assets.model import AdAssetTarget, AdAssetType
from app.HelperModules.Collections.dzgro.adv.rule_runs.model import AdRuleRunStatus
from app.HelperModules.Collections.dzgro.adv.rules.model import AdCriteriaResultAction, AdCriteriaResultSubAction
from app.HelperModules.Collections.dzgro.adv.rules.model import AdRule
from app.HelperModules.Collections.dzgro.model import Operator
from app.HelperModules.Helpers.Date import DateHelper
from app.HelperModules.Pipelines.Marketplace.PipelineProcessor import LookUpLetExpression, LookUpPipelineMatchExpression, PipelineProcessor
from app.HelperModules.Pipelines.Marketplace.Pipelines.DataTransformer import Datatransformer
from app.routers.ad.models.sp import AdGroupThemeBasedBidRecommendationRequestV4, BidRecommendationPerTargetingExpressionV4, BidValue, SponsoredProductsBulkKeywordOperationResponse, SponsoredProductsUpdateSponsoredProductsKeywordsRequestContent
from app.HelperModules.Collections.accounts.marketplaces.model import AdvertisingAccount, BidMinMax, MarketplaceWithTokens
from app.HelperModules.Collections.dzgro.adv.assets.Helper import AdvertisementHelper

class TargetRuleExecutor:
    marketplace: ObjectId
    uid: str
    runid: str
    adv: AdvertisementHelper
    pp: PipelineProcessor


    def __init__(self, marketplace: ObjectId, uid: str, runid: str) -> None:
        self.marketplace = marketplace
        self.uid = uid
        self.runid = runid
        self.pp = PipelineProcessor(self.marketplace, self.uid)
        self.adv = AdvertisementHelper(self.marketplace, self.uid)

    # def addBidRanges(self):
    #     def getBidSuggestions(req: AdGroupThemeBasedBidRecommendationRequestV4)->list[BidRecommendationPerTargetingExpressionV4]:
    #         try:
    #             response = utility.getSPTargeBidRecommendations(req)
    #             return response.bidRecommendations[0].bidRecommendationsForTargetingExpressions
    #         except Exception as e:
    #             error:AmazonApiResponse =  e.args[0]
    #             if error.statusCode==429:
    #                 time.sleep(2)
    #                 return getBidSuggestions(req)
    #             return []
        
    #     utility = AdUtility(account = self.account)
    #     pipeline = [{ '$match': { 'marketplace': self.marketplace.id, 'bidValues': { '$exists': False }, "negative": False } },{ '$lookup': { 'from': 'adv_rule_results', 'let': { 'runId': self.run.id, 'marketplace': '$marketplace', 'id': '$_id' }, 'pipeline': [ { '$match': { '$expr': { '$and': [ { '$eq': [ '$id', '$$id' ] }, { '$eq': [ '$runId', '$$runId' ] }, { '$eq': [ '$marketplace', '$$marketplace' ] } ] } } } ], 'as': 'performance' } }, { '$set': { 'performance': { '$first': '$performance' } } }, { '$match': { 'performance': { '$exists': True } } }, { '$set': { 'type': { '$switch': { 'branches': [ { 'case': { '$eq': [ '$targetDetails.matchType', 'PRODUCT_SUBSTITUTES' ] }, 'then': { 'type': 'SUBSTITUTES' } }, { 'case': { '$eq': [ '$targetDetails.matchType', 'PRODUCT_COMPLEMENTS' ] }, 'then': { 'type': 'COMPLEMENTS' } }, { 'case': { '$eq': [ '$targetDetails.matchType', 'SEARCH_LOOSE_MATCH' ] }, 'then': { 'type': 'LOOSE_MATCH' } }, { 'case': { '$eq': [ '$targetDetails.matchType', 'SEARCH_CLOSE_MATCH' ] }, 'then': { 'type': 'CLOSE_MATCH' } }, { 'case': { '$in': [ '$targetDetails.matchType', [ 'PRODUCT_EXACT', 'PRODUCT_SIMILAR' ] ] }, 'then': { 'type': 'PAT_ASIN', 'value': '$targetDetails.asin' } }, { 'case': { '$eq': [ '$targetDetails.matchType', 'PRODUCT_CATEGORY' ] }, 'then': { 'type': 'PAT_CATEGORY', 'value': '$targetDetails.productCategoryId' } }, { 'case': { '$eq': [ '$targetDetails.matchType', 'EXACT' ] }, 'then': { 'type': 'KEYWORD_EXACT_MATCH', 'value': '$targetDetails.keyword' } }, { 'case': { '$eq': [ '$targetDetails.matchType', 'BROAD' ] }, 'then': { 'type': 'KEYWORD_BROAD_MATCH', 'value': '$targetDetails.keyword' } }, { 'case': { '$eq': [ '$targetDetails.matchType', 'PHRASE' ] }, 'then': { 'type': 'KEYWORD_PHRASE_MATCH', 'value': '$targetDetails.keyword' } } ], 'default': None } } } }, { '$set': { 'type.id': '$_id' } }, { '$group': { '_id': { 'adGroupId': '$adGroupId', 'campaignId': '$campaignId' }, 'types': { '$push': '$type' } } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$_id', { 'recommendationType': 'BIDS_FOR_EXISTING_AD_GROUP', 'targetingExpressions': '$types' } ] } } } ]
    #     response = list(mongo_db.dzgro.adv_targets.aggregate(pipeline))
    #     bidsMapping: dict[str, list[dict]] = {}
    #     for res in response: 
    #         adGroupBids = getBidSuggestions(AdGroupThemeBasedBidRecommendationRequestV4(**res))
    #         for tx in res['targetingExpressions']:
    #             targetType, matchType, targetId = tx.get('type',None), tx.get('value',None), str(tx.get('id',None))
    #             for x in adGroupBids:
    #                 txBid = json.loads(x.targetingExpression.model_dump_json())
    #                 xTargetType, xMatchType = txBid.get('type',None), txBid.get('value',None)
    #                 if targetType==xTargetType:
    #                     if not matchType: bidsMapping[targetId]=[x.model_dump() for x in x.bidValues]
    #                     elif matchType==xMatchType: bidsMapping[targetId]=[x.model_dump() for x in x.bidValues]
    #     pipeline = [ { '$match': { "marketplace": self.marketplace.id, '_id': {"$in": list(bidsMapping.keys())} } }, { '$replaceRoot': { 'newRoot': { '$mergeObjects': [ '$$ROOT', { 'bidValues': { '$getField': { 'input': bidsMapping, 'field': { '$toString': '$_id' } } } } ] } } }, { '$merge': 'adv_targets' } ]
    #     mongo_db.dzgro.adv_targets.aggregate(pipeline)
    #     res = mongo_db.dzgro.adv_rule_runs.update_one({"_id": self.run.id,"marketplace": self.marketplace.id}, {"$set": {"completedAt": datetime.now()}})
