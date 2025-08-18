from bson import ObjectId
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.db.collections.pipelines.ad_structure import GetStructureScore, GetAdGroupsViolations, GetAdsForAdGroup, GetMatchTypesForAdGroup, GetTargetsForAdGroup
from dzgroshared.models.enums import CollectionType
from dzgroshared.models.extras.ad_structure import AdGroupOptimizationRequest, AdGroupOptimizationResponse, RemoveMultipleAdsForm, RemoveMatchTypesForm, RemoveKeywordStuffingForm
from dzgroshared.db.client import DbClient
from dzgroshared.client import DzgroSharedClient

class AdStructureHelper:
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.marketplace = marketplace
        self.db = DbManager(client.db.database.get_collection(CollectionType.ADV_ASSETS.value), uid, marketplace)

    async def getAdvertismentStructureScore(self):
        pipeline = GetStructureScore.pipeline(self.uid, self.marketplace)
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("No Data to Display")
        return data[0]
        
    async def getAdGroupWithStructureViolations(self):
        pipeline = GetAdGroupsViolations.pipeline(self.uid, self.marketplace)
        return await self.db.aggregate(pipeline)
    
    async def getAdGroupViolation(self, adgroupid: str):
        pipeline = GetAdGroupsViolations.pipeline(self.uid, self.marketplace, adgroupid)
        data = await self.db.aggregate(pipeline)
        if len(data)==0: raise ValueError("Ad Group is inactive or not delivering")
        return data[0]
    
    async def getMultipleAsinViolationByAdgroupId(self, adgroup:str):
        pipeline = GetAdsForAdGroup.pipeline(self.uid, self.marketplace, adgroup)
        data = await self.db.aggregate(pipeline)
        return data
    
    async def getMatchTypesForAdGroup(self, adgroup:str):
        pipeline = GetMatchTypesForAdGroup.pipeline(self.uid, self.marketplace, adgroup)
        data = await self.db.aggregate(pipeline)
        return data
    
    async def getTargetsForAdGroup(self, adgroup:str, matchtype:str|None):
        pipeline = GetTargetsForAdGroup.pipeline(self.uid, self.marketplace, adgroup, matchtype)
        data = await self.db.aggregate(pipeline)
        return data

    async def optimiseAdGroup(self, request: AdGroupOptimizationRequest) -> AdGroupOptimizationResponse:
        try:
            changes_applied = {}
            
            # Process multiple ads removal if provided
            if request.ads:
                changes_applied["multiple_ads"] = await self._processMultipleAdsOptimization(
                    request.adgroupid, 
                    request.ads
                )
            
            # Process match types removal if provided
            if request.matchtypes:
                changes_applied["match_types"] = await self._processMatchTypesOptimization(
                    request.adgroupid, 
                    request.matchtypes
                )
            
            # Process keyword stuffing removal if provided
            if request.targets:
                changes_applied["keyword_stuffing"] = await self._processKeywordStuffingOptimization(
                    request.adgroupid, 
                    request.targets
                )
            
            return AdGroupOptimizationResponse(
                success=True,
                message=f"Ad group {request.adgroupid} optimized successfully",
                adgroupid=request.adgroupid,
                changes_applied=changes_applied
            )
            
        except Exception as e:
            return AdGroupOptimizationResponse(
                success=False,
                message=f"Failed to optimize ad group {request.adgroupid}: {str(e)}",
                adgroupid=request.adgroupid,
                changes_applied={}
            )

    async def _processMultipleAdsOptimization(self, adgroupid: str, config: RemoveMultipleAdsForm) -> dict:
        """Process multiple ads optimization"""
        changes = {
            "ads_retained": len(config.retain),
            "ads_paused": len(config.pause),
            "ads_created_new": len(config.createNew),
            "retained_ad_ids": [ad.ad for ad in config.retain],
            "paused_ad_ids": [ad.ad for ad in config.pause],
            "new_ad_ids": [ad.ad for ad in config.createNew]
        }
        
        # TODO: Implement actual ad optimization logic
        # This would involve updating the ad group structure in the database
        
        return changes

    async def _processMatchTypesOptimization(self, adgroupid: str, config: RemoveMatchTypesForm) -> dict:
        """Process match types optimization"""
        changes = {
            "match_types_retained": len(config.retain),
            "match_types_paused": len(config.pause),
            "match_types_created_new": len(config.createNew),
            "retained_match_types": [mt.matchtype for mt in config.retain],
            "paused_match_types": [mt.matchtype for mt in config.pause],
            "new_match_types": [mt.matchtype for mt in config.createNew]
        }
        
        # Extract target information from match types with targets
        all_targets_to_retain = []
        all_targets_to_pause = []
        all_targets_to_create_new = []
        
        # Collect targets from retained match types
        for mt in config.retain:
            all_targets_to_retain.extend([target.id for target in mt.targetsToRetain])
            all_targets_to_pause.extend([target.id for target in mt.targetsToPause])
            all_targets_to_create_new.extend([target.id for target in mt.targetsToCreateNew])
        
        # Collect targets from paused match types
        for mt in config.pause:
            all_targets_to_retain.extend([target.id for target in mt.targetsToRetain])
            all_targets_to_pause.extend([target.id for target in mt.targetsToPause])
            all_targets_to_create_new.extend([target.id for target in mt.targetsToCreateNew])
        
        # Collect targets from new match types
        for mt in config.createNew:
            all_targets_to_retain.extend([target.id for target in mt.targetsToRetain])
            all_targets_to_pause.extend([target.id for target in mt.targetsToPause])
            all_targets_to_create_new.extend([target.id for target in mt.targetsToCreateNew])
        
        # Add target summary to changes
        changes["targets_from_match_types"] = {
            "targets_to_retain": all_targets_to_retain,
            "targets_to_pause": all_targets_to_pause,
            "targets_to_create_new": all_targets_to_create_new,
            "total_targets_to_retain": len(all_targets_to_retain),
            "total_targets_to_pause": len(all_targets_to_pause),
            "total_targets_to_create_new": len(all_targets_to_create_new)
        }
        
        # TODO: Implement actual match type optimization logic
        # This would involve updating the match type structure in the database
        
        return changes

    async def _processKeywordStuffingOptimization(self, adgroupid: str, config: RemoveKeywordStuffingForm) -> dict:
        """Process keyword stuffing optimization"""
        changes = {
            "targets_retained": len(config.retain),
            "targets_paused": len(config.pause),
            "targets_created_new": len(config.createNew),
            "retained_target_ids": [target.id for target in config.retain],
            "paused_target_ids": [target.id for target in config.pause],
            "new_target_ids": [target.id for target in config.createNew]
        }
        
        # TODO: Implement actual target optimization logic
        # This would involve updating the target structure in the database
        
        return changes