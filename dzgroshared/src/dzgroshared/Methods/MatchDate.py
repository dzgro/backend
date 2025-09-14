from app.HelperModules.Collections.accounts.marketplaces.model import Timezone

def matchDate(noOfDays: int, timezone: Timezone):
    return {
        '$match': {
            '$expr': {
                '$let': {
                    'vars': {
                        'dates': {
                            '$let': {
                                'vars': {
                                    'curr': {
                                        '$dateFromString': {
                                            'dateString': {
                                                '$dateToString': {
                                                    'date': {
                                                        '$dateSubtract': {
                                                            'startDate': '$$NOW', 
                                                            'unit': 'day', 
                                                            'amount': 1, 
                                                            'timezone': timezone
                                                        }
                                                    }, 
                                                    'format': '%Y-%m-%d'
                                                }
                                            }
                                        }
                                    }
                                }, 
                                'in': {
                                    '$reduce': {
                                        'input': {
                                            '$range': [
                                                0, noOfDays, 1
                                            ]
                                        }, 
                                        'initialValue': [], 
                                        'in': {
                                            '$concatArrays': [
                                                '$$value', [
                                                    {
                                                        '$dateSubtract': {
                                                            'startDate': '$$curr', 
                                                            'unit': 'day', 
                                                            'amount': '$$this'
                                                        }
                                                    }
                                                ]
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                    }, 
                    'in': {
                        '$in': [
                            '$date', '$$dates'
                        ]
                    }
                }
            }
        }
    }