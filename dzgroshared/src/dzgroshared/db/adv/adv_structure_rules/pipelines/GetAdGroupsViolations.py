from bson import ObjectId

def pipeline(marketplace: ObjectId,adgroupId: str|None=None):
    matchStage = {
    "$match": {
      "marketplace": marketplace,
      "assettype": "Ad Group",
      "id": adgroupId,
      "state": "ENABLED",
      "adproduct": "SPONSORED_PRODUCTS"
    }
  }
    if not adgroupId: del matchStage["$match"]["id"]
    return [matchStage,
  {
    "$match": {
      "marketplace": marketplace,
      "assettype": "Ad Group",
      "state": "ENABLED",
      "adproduct": "SPONSORED_PRODUCTS"
    }
  },
  {
    "$lookup": {
      "from": "adv_assets",
      "let": {
        "marketplace": "$marketplace",
        "adgroupid": "$id"
      },
      "pipeline": [
        {
          "$match": {
            "$expr": {
              "$and": [
                {
                  "$eq": [
                    "$marketplace",
                    "$$marketplace"
                  ]
                },
                {
                  "$eq": [
                    "$assettype",
                    "Ad"
                  ]
                },
                {
                  "$eq": [
                    "$parent",
                    "$$adgroupid"
                  ]
                },
                {
                  "$eq": [
                    "$state",
                    "ENABLED"
                  ]
                },
                {
                  "$eq": [
                    "$deliverystatus",
                    "DELIVERING"
                  ]
                },
                {
                  "$eq": [
                    "$adproduct",
                    "SPONSORED_PRODUCTS"
                  ]
                },
              ]
            }
          }
        },
        {
          "$unwind": "$creative.products"
        },
        {
          "$match": {
            "creative.products.productIdType": "ASIN"
          }
        },
        {
          "$group": {
            "_id": "$parent",
            "asinSet": {
              "$addToSet": "$creative.products.productId"
            }
          }
        }
      ],
      "as": "adsData"
    }
  },
  {
    "$addFields": {
      "violatesMultipleProducts": {
        "$gt": [
          {
            "$size": {
              "$ifNull": [
                {
                  "$arrayElemAt": [
                    "$adsData.asinSet",
                    0
                  ]
                },
                []
              ]
            }
          },
          1
        ]
      }
    }
  },
  {
    "$lookup": {
      "from": "adv_assets",
      "let": {
        "uid": "$uid",
        "marketplace": "$marketplace",
        "adgroupid": "$id"
      },
      "pipeline": [
        {
          "$match": {
            "$expr": {
              "$and": [
                {
                  "$eq": [
                    "$uid",
                    "$$uid"
                  ]
                },
                {
                  "$eq": [
                    "$marketplace",
                    "$$marketplace"
                  ]
                },
                {
                  "$eq": [
                    "$assettype",
                    "Target"
                  ]
                },
                {
                  "$eq": [
                    "$state",
                    "ENABLED"
                  ]
                },
                {
                  "$eq": [
                    "$deliverystatus",
                    "DELIVERING"
                  ]
                },
                {
                  "$eq": [
                    "$adproduct",
                    "SPONSORED_PRODUCTS"
                  ]
                },
                {
                  "$eq": [
                    "$negative",
                    False
                  ]
                },
                {
                  "$eq": [
                    "$parent",
                    "$$adgroupid"
                  ]
                }
              ]
            }
          }
        },
        {
          "$group": {
            "_id": "$parent",
            "matchTypes": {
              "$addToSet": "$targetdetails.matchType"
            },
            "targetCount": {
              "$sum": 1
            }
          }
        }
      ],
      "as": "targetingData"
    }
  },
  {
    "$addFields": {
      "violatesMultipleMatchTypes": {
        "$gt": [
          {
            "$size": {
              "$ifNull": [
                {
                  "$arrayElemAt": [
                    "$targetingData.matchTypes",
                    0
                  ]
                },
                []
              ]
            }
          },
          1
        ]
      },
      "violatesKeywordStuffing": {
        "$gt": [
          {
            "$ifNull": [
              {
                "$arrayElemAt": [
                  "$targetingData.targetCount",
                  0
                ]
              },
              0
            ]
          },
          10
        ]
      }
    }
  },
  {
    "$lookup": {
      "from": "adv_assets",
      "let": {
        "uid": "$uid",
        "marketplace": "$marketplace",
        "cid": "$campaignid"
      },
      "pipeline": [
        {
          "$match": {
            "$expr": {
              "$and": [
                {
                  "$eq": [
                    "$uid",
                    "$$uid"
                  ]
                },
                {
                  "$eq": [
                    "$marketplace",
                    "$$marketplace"
                  ]
                },
                {
                  "$eq": [
                    "$assettype",
                    "Campaign"
                  ]
                },
                {
                  "$eq": [
                    "$id",
                    "$$cid"
                  ]
                }
              ]
            }
          }
        },
        {
          "$project": {
            "name": 1
          }
        }
      ],
      "as": "campaignInfo"
    }
  },
  {
    "$addFields": {
      "campaignName": {
        "$ifNull": [
          {
            "$arrayElemAt": [
              "$campaignInfo.name",
              0
            ]
          },
          ""
        ]
      }
    }
  },
  {
    "$project": {
      "_id": 0,
      "adgroupid": "$id",
      "name": 1,
      "campaignid": 1,
      "campaignName": 1,
      "violatesMultipleProducts": 1,
      "violatesMultipleMatchTypes": 1,
      "violatesKeywordStuffing": 1
    }
  },
  {
    "$match": {
      "$or": [
        {"violatesMultipleProducts": True},
        {"violatesMultipleMatchTypes": True},
        {"violatesKeywordStuffing": True}
      ]
    }
  }
]