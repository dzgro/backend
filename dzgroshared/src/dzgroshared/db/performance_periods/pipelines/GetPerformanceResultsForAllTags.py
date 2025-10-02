from bson import ObjectId
from dzgroshared.db.PipelineProcessor import PipelineProcessor
from dzgroshared.db.enums import CollateType
from dzgroshared.analytics import controller
from dzgroshared.db.model import PeriodDataRequest

def getPeriodPerformance(collatetype: CollateType, value: str|None):
    return [{
        "$lookup": {
                        'from': 'performance_period_results', 
                        'let': {
                            'queryid': '$_id', 
                            'collatetype': collatetype.value,
                            'value': value
                        }, 
                        'pipeline': [
                            {
                                '$match': {
                                    '$expr': {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$queryid', '$$queryid'
                                                ]
                                            }, {
                                                '$eq': [
                                                    '$collatetype', '$$collatetype'
                                                ]
                                            }, True if not value else {
                                                '$eq': [
                                                    '$value', '$$value'
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }, {
            "$replaceWith": "$data"
          }
                        ], 
                        'as': 'data'
                    }
    },
    
    {
        "$unwind": "$data"
    }
    ]

def pipeline(marketplace: ObjectId, req: PeriodDataRequest):
    pipeline = [{"$match": {"marketplace": marketplace}}]
    pipeline.extend(getPeriodPerformance(req.collatetype, req.value))
    return pipeline