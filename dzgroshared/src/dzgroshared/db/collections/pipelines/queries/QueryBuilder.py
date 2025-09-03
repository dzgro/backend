from dzgroshared.models.enums import QueryMetricName

ad_fields = [
    {"label": "Impressions", "key": "impressions", "desc": "Total number of times ads were shown"},
    {"label": "Clicks", "key": "clicks", "desc": "Total number of times ads were clicked"},
    {"label": "CTR %", "key": "ctr", "desc": "Percentage of clicks received out of total impressions", "derived": True},
    {"label": "Ad Spend", "key": "cost", "desc": "Cost incurred for ads"},
    {"label": "CPC", "key": "cpc", "desc": "Average cost spent for each click", "derived": True},
    {"label": "Ad Units", "key": "units", "desc": "Total number of items sold through ads"},
    {"label": "CVR %", "key": "cvr", "desc": "Percentage of clicks that resulted in a purchase", "derived": True},
    {"label": "Ad Sales", "key": "sales", "desc": "Revenue generated from ads"},
    {"label": "ACOS %", "key": "acos", "desc": "Cost spent on advertising as a percentage of revenue generated from ads", "derived": True},
    {"label": "ROAS", "key": "roas", "desc": "Revenue generated for every unit of ad cost", "derived": True},
    {"label": "Ad Spend/Unit", "key": "adspendperunit", "desc": "Average ad cost per item sold", "derived": True}
]

sales_fields = [
    {"label": "Net Revenue", "key": "revenue", "desc": "Total value of orders after returns including tax"},
    {"label": "Gross Revenue", "key": "ordervalue", "desc": "Total value of purchases including tax", "derived": True},
    {"label": "Returned Revenue", "key": "returnordervalue", "desc": "Total value of returned purchases including tax", "derived": True},
    {"label": "TACoS %", "key": "tacos", "desc": "Ad cost as a percentage of total revenue"},
    {"label": "Organic Sales %", "key": "organicsalespercent", "desc": "Percentage of revenue generated from non-ad sources"},
    {"label": "Quantity", "key": "quantity", "desc": "Total items purchased"},
    {"label": "Return Quantity", "key": "returnquantity", "desc": "Items returned by customers", "derived": True},
    {"label": "Net Quantity", "key": "netquantity", "desc": "Net items sold after returns", "derived": True},
    {"label": "Return %", "key": "returnpercent", "desc": "Items returned as a percentage of total items sold", "derived": True},
    {"label": "Average Selling Price", "key": "asp", "desc": "Average selling price of items sold", "derived": True},
    {"label": "Expenses", "key": "expenses", "desc": "Total Expenses"},
    {"label": "Fees", "key": "fees", "desc": "Fees charged by the platform", "derived": True},
    {"label": "Other Expenses", "key": "otherexpenses", "desc": "Additional adjustments or costs", "derived": True},
    {"label": "Net Payout", "key": "netproceeds", "desc": "Net revenue after fees, returns, and adjustments"},
    {"label": "Net Payout/Unit", "key": "netpayoutperunit", "desc": "Average net revenue earned per item sold", "derived": True},
    {"label": "Net Payout %", "key": "netpayoutpercent", "desc": "Net revenue as a percentage of total order value", "derived": True}
]

traffic_fields = [
    {"label": "Buy Box %", "key": "buyboxviewpercent", "desc": "% times the featured offer was with your brand"},
    {"label": "Page Views", "key": "pageviews", "desc": "Total number of pages viewed"},
    {"label": "Browser Page Views", "key": "browserpageviews", "desc": "Pages viewed from web browsers", "derived": True},
    {"label": "Browser Page View %", "key": "browserpageviewpercent", "desc": "Browser page views as a percentage of total page views", "derived": True},
    {"label": "Mobile App Page Views", "key": "mobileapppageviews", "desc": "Pages viewed from mobile apps", "derived": True},
    {"label": "Mobile App Page View %", "key": "mobileapppageviewpercent", "desc": "Mobile app page views as a percentage of total page views", "derived": True},
    {"label": "Unit Session %", "key": "unitsessionpercent", "desc": "Percentage of sessions that resulted in a purchase"},
    {"label": "Sessions", "key": "sessions", "desc": "Total number of user sessions"},
    {"label": "Browser Sessions", "key": "browsersessions", "desc": "Sessions originating from web browsers", "derived": True},
    {"label": "Mobile App Sessions", "key": "mobileappsessions", "desc": "Sessions originating from mobile applications", "derived": True},
    {"label": "Browser Session %", "key": "browsersessionpercent", "desc": "Browser sessions as a percentage of total sessions", "derived": True},
    {"label": "Mobile App Session %", "key": "mobileappsessionpercent", "desc": "Mobile app sessions as a percentage of total sessions", "derived": True},

]


percent_fields = [
        "ctr", "cvr", "acos", "netpayoutpercent", "unitsessionpercent",
        "browsersessionpercent", "mobileappsessionpercent",
        "browserpageviewpercent", "mobileapppageviewpercent",
        "buyboxviewpercent", "tacos", "adsalespercent", "organicsalespercent","returnpercent"
    ]
non_percent_fields = [
                  "clicks","impressions","orders","sessions","units","quantity","returnquantity",
                  "pageviews","browsersessions","browserpageviews","mobileappsessions",
                  "mobileapppageviews","buyboxviews","netquantity",
                  "cost","sales","ordervalue","netproceeds","fees","returnvalue","ordertax",
                  "otherexpenses","roas","expenses","units"
                ]

def addMissingFields(data_key: str = "data"):
    return {
    "$addFields": {
      f"{data_key}.impressions": { "$ifNull": [f"${data_key}.impressions", 0] },
      f"{data_key}.clicks": { "$ifNull": [f"${data_key}.clicks", 0] },
      f"{data_key}.cost": { "$ifNull": [f"${data_key}.cost", 0] },
      f"{data_key}.orders": { "$ifNull": [f"${data_key}.orders", 0] },
      f"{data_key}.sales": { "$ifNull": [f"${data_key}.sales", 0] },
      f"{data_key}.units": { "$ifNull": [f"${data_key}.units", 0] },
      f"{data_key}.ordervalue": { "$ifNull": [f"${data_key}.ordervalue", 0] },
      f"{data_key}.ordertax": { "$ifNull": [f"${data_key}.ordertax", 0] },
      f"{data_key}.quantity": { "$ifNull": [f"${data_key}.quantity", 0] },
      f"{data_key}.returnQuantity": { "$ifNull": [f"${data_key}.returnQuantity", 0] },
      f"{data_key}.returnvalue": { "$ifNull": [f"${data_key}.returnvalue", 0] },
      f"{data_key}.netproceeds": { "$ifNull": [f"${data_key}.netproceeds", 0] },
      f"{data_key}.fees": { "$ifNull": [f"${data_key}.fees", 0] },
      f"{data_key}.otherexpenses": { "$ifNull": [f"${data_key}.otherexpenses", 0] },
      f"{data_key}.sessions": { "$ifNull": [f"${data_key}.sessions", 0] },
      f"{data_key}.pageviews": { "$ifNull": [f"${data_key}.pageviews", 0] },
      f"{data_key}.unitsessions": { "$ifNull": [f"${data_key}.unitsessions", 0] },
      f"{data_key}.browsersessions": { "$ifNull": [f"${data_key}.browsersessions", 0] },
      f"{data_key}.browserpageviews": { "$ifNull": [f"${data_key}.browserpageviews", 0] },
      f"{data_key}.mobileappsessions": { "$ifNull": [f"${data_key}.mobileappsessions", 0] },
      f"{data_key}.mobileapppageviews": { "$ifNull": [f"${data_key}.mobileapppageviews", 0] },
      f"{data_key}.buyboxviews": { "$ifNull": [f"${data_key}.buyboxviews", 0] }
    }
  }

def addDerivedMetrics(data_key: str = "data"):
    dk = f"${data_key}."
    return [
        {
            "$addFields": {
                # ---- ad metrics ----
                f"{data_key}.ctr": {
                    "$cond": [
                        {"$gt": [f"{dk}impressions", 0]},
                        {"$round": [
                            {"$multiply": [
                                {"$divide": [f"{dk}clicks", f"{dk}impressions"]}, 100
                            ]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.cpc": {
                    "$cond": [
                        {"$gt": [f"{dk}clicks", 0]},
                        {"$round": [
                            {"$divide": [f"{dk}cost", f"{dk}clicks"]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.cvr": {
                    "$cond": [
                        {"$gt": [f"{dk}clicks", 0]},
                        {"$round": [
                            {"$multiply": [
                                {"$divide": [f"{dk}units", f"{dk}clicks"]}, 100
                            ]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.acos": {
                    "$cond": [
                        {"$gt": [f"{dk}sales", 0]},
                        {"$round": [
                            {"$multiply": [
                                {"$divide": [f"{dk}cost", f"{dk}sales"]}, 100
                            ]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.roas": {
                    "$cond": [
                        {"$gt": [f"{dk}cost", 0]},
                        {"$round": [
                            {"$divide": [f"{dk}sales", f"{dk}cost"]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.adspendperunit": {
                    "$cond": [
                        {"$gt": [f"{dk}units", 0]},
                        {"$round": [
                            {"$divide": [f"{dk}cost", f"{dk}units"]}, 2
                        ]},
                        0
                    ]
                },

                # ---- sales metrics ----
                f"{data_key}.netquantity": {
                    "$subtract": [
                        {"$ifNull": [f"{dk}quantity", 0]},
                        {"$ifNull": [f"{dk}returnquantity", 0]}
                    ]
                },
                f"{data_key}.returnpercent": {
                    "$cond": [
                        {"$gt": [f"{dk}quantity", 0]},
                        {"$round": [
                            {"$multiply": [
                                {"$divide": [f"{dk}returnquantity", f"{dk}quantity"]}, 100
                            ]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.revenue": {
                    "$add": [
                        {"$ifNull": [f"{dk}ordervalue", 0]},
                        {"$ifNull": [f"{dk}returnordervalue", 0]}
                    ]
                },
                f"{data_key}.asp": {
                    "$add": [
                        {"$ifNull": [f"{dk}ordervalue", 0]},
                        {"$ifNull": [f"{dk}quantity", 0]}
                    ]
                },
                f"{data_key}.netpayoutperunit": {
                    "$cond": [
                        {"$gt": [f"{dk}quantity", 0]},
                        {"$round": [
                            {"$divide": [f"{dk}netproceeds", f"{dk}quantity"]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.netpayoutpercent": {
                    "$cond": [
                        {"$gt": [f"{dk}ordervalue", 0]},
                        {"$round": [
                            {"$multiply": [
                                {"$divide": [f"{dk}netproceeds", f"{dk}ordervalue"]}, 100
                            ]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.expenses": {
                    "$add": [
                        {"$ifNull": [f"{dk}fees", 0]},
                        {"$ifNull": [f"{dk}otherexpenses", 0]}
                    ]
                },

                # ---- traffic metrics ----
                f"{data_key}.unitsessionpercent": {
                    "$cond": [
                        {"$gt": [f"{dk}sessions", 0]},
                        {"$round": [
                            {"$multiply": [
                                {"$divide": [f"{dk}unitsessions", f"{dk}sessions"]}, 100
                            ]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.browsersessionpercent": {
                    "$cond": [
                        {"$gt": [f"{dk}sessions", 0]},
                        {"$round": [
                            {"$multiply": [
                                {"$divide": [f"{dk}browsersessions", f"{dk}sessions"]}, 100
                            ]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.mobileappsessionpercent": {
                    "$cond": [
                        {"$gt": [f"{dk}sessions", 0]},
                        {"$round": [
                            {"$multiply": [
                                {"$divide": [f"{dk}mobileappsessions", f"{dk}sessions"]}, 100
                            ]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.browserpageviewpercent": {
                    "$cond": [
                        {"$gt": [f"{dk}pageviews", 0]},
                        {"$round": [
                            {"$multiply": [
                                {"$divide": [f"{dk}browserpageviews", f"{dk}pageviews"]}, 100
                            ]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.mobileapppageviewpercent": {
                    "$cond": [
                        {"$gt": [f"{dk}pageviews", 0]},
                        {"$round": [
                            {"$multiply": [
                                {"$divide": [f"{dk}mobileapppageviews", f"{dk}pageviews"]}, 100
                            ]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.buyboxviewpercent": {
                    "$cond": [
                        {"$gt": [f"{dk}pageviews", 0]},
                        {"$round": [
                            {"$multiply": [
                                {"$divide": [f"{dk}buyboxviews", f"{dk}pageviews"]}, 100
                            ]}, 2
                        ]},
                        0
                    ]
                },

                # ---- cross functional ----
                f"{data_key}.tacos": {
                    "$cond": [
                        {"$gt": [f"{dk}ordervalue", 0]},
                        {"$round": [
                            {"$subtract": [f"{dk}ordervalue", f"{dk}ordertax"]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.pretaxrevenue": {
                    "$cond": [
                        {"$gt": [f"{dk}ordervalue", 0]},
                        {"$round": [
                            {"$multiply": [
                                {"$divide": [f"{dk}cost", f"{dk}ordervalue"]}, 100
                            ]}, 2
                        ]},
                        0
                    ]
                },
                f"{data_key}.organicsalespercent": {
                    "$cond": [
                        {"$gt": [f"{dk}pretaxrevenue", 0]},
                        {"$round": [
                            {"$multiply": [
                                {"$divide": [
                                    {"$subtract": [f"{dk}pretaxrevenue", f"{dk}sales"]},
                                    f"{dk}pretaxrevenue"
                                ]}, 100
                            ]}, 2
                        ]},
                        0
                    ]
                }
            }
        }
    ]


def build_transformation_pipeline(is_india: bool = False, data_key: str = "data"):
    # everything else treated as non-percent
    # (we don’t need to explicitly list all because transformation covers all keys)
    
    # Indian vs Global scales
    india_labels = ["Cr", "L", "K"]
    global_labels = ["Bn", "M", "K"]
    labels = india_labels if is_india else global_labels
    scale_divs = [10000000, 100000, 1000] if is_india else [1_000_000_000, 1_000_000, 1000]

    return [
        {
            "$addFields": {
                data_key: {
                    "$map": {
                        "input": {"$objectToArray": f"${data_key}"},
                        "as": "kv",
                        "in": {
                            "k": "$$kv.k",
                            "v": {
                                "$let": {
                                    "vars": {
                                        "val": "$$kv.v",
                                        "isPercent": {"$in": ["$$kv.k", percent_fields]}
                                    },
                                    "in": {
                                        "$cond": [
                                            "$$isPercent",
                                            {  # Percent fields
                                                "value": {
                                                    "$concat": [
                                                        {
                                                            "$cond": [
                                                                {"$lt": ["$$val", 10]},
                                                                {"$toString": {"$round": ["$$val", 2]}},
                                                                {"$toString": {"$round": ["$$val", 1]}}
                                                            ]
                                                        },
                                                        "%"
                                                    ]
                                                },
                                                "rawvalue": {"$round": ["$$val", 2]}
                                            },
                                            {  # Non-percent fields
                                                "$let": {
                                                    "vars": {
                                                        "rounded": {
                                                            "$cond": [
                                                                {"$gte": ["$$val", 100]},
                                                                {"$round": ["$$val", 0]},
                                                                {"$round": ["$$val", 1]}
                                                            ]
                                                        }
                                                    },
                                                    "in": {
                                                        "$let": {
                                                            "vars": {
                                                                "scaled": {
                                                                    "$switch": {
                                                                        "branches": [
                                                                            {
                                                                                "case": {"$gte": ["$$val", scale_divs[0]]},
                                                                                "then": {
                                                                                    "$concat": [
                                                                                        {"$toString": {"$round": [{"$divide": ["$$val", scale_divs[0]]}, 2]}},
                                                                                        f" {labels[0]}"
                                                                                    ]
                                                                                }
                                                                            },
                                                                            {
                                                                                "case": {"$gte": ["$$val", scale_divs[1]]},
                                                                                "then": {
                                                                                    "$concat": [
                                                                                        {"$toString": {"$round": [{"$divide": ["$$val", scale_divs[1]]}, 2]}},
                                                                                        f" {labels[1]}"
                                                                                    ]
                                                                                }
                                                                            },
                                                                            {
                                                                                "case": {"$gte": ["$$val", scale_divs[2]]},
                                                                                "then": {
                                                                                    "$concat": [
                                                                                        {"$toString": {"$round": [{"$divide": ["$$val", scale_divs[2]]}, 2]}},
                                                                                        f" {labels[2]}"
                                                                                    ]
                                                                                }
                                                                            }
                                                                        ],
                                                                        "default": {"$toString": "$$rounded"}
                                                                    }
                                                                }
                                                            },
                                                            "in": {
                                                                "value": "$$scaled",
                                                                "rawvalue": "$$rounded"
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        {
            "$addFields": {
                data_key: {"$arrayToObject": f"${data_key}"}
            }
        }
    ]

def addGrowth():
    return {
    "$addFields": {
      "growth": {
        "$arrayToObject": {
          "$map": {
            "input": { "$objectToArray": "$curr" },
            "as": "kv",
            "in": {
              "k": "$$kv.k",
              "v": {
                  "$let": {
                    "vars": {
                      "currVal": "$$kv.v.rawvalue",
                      "preVal": {
                        "$getField": {
                          "input": {
                            "$getField": {
                              "field": "$$kv.k",
                              "input": "$pre"
                            }
                          },
                          "field": "rawvalue"
                        }
                      },
                      "percentFields": percent_fields
                    },
                    "in": {
                      "$cond": [
                        { "$in": ["$$kv.k", "$$percentFields"] },
                        
                        {
                                "$cond": [
                                  { "$lt": [{ "$abs": { "$subtract": ["$$currVal", "$$preVal"] } }, 10] },
                                  { "$round": [{ "$subtract": ["$$currVal", "$$preVal"] }, 2] },
                                  { "$round": [{ "$subtract": ["$$currVal", "$$preVal"] }, 1] }
                                ]
                              },
                        
                        {
                                "$cond": [
                                  { "$or": [{ "$eq": ["$$preVal", 0] }, { "$eq": ["$$preVal", None] }] },
                                  0,
                                  {
                                    "$cond": [
                                      {
                                        "$lt": [
                                          {
                                            "$abs": {
                                              "$multiply": [
                                                { "$divide": [{ "$subtract": ["$$currVal", "$$preVal"] }, "$$preVal"] },
                                                100
                                              ]
                                            }
                                          },
                                          10
                                        ]
                                      },
                                      {
                                        "$round": [
                                          {
                                            "$multiply": [
                                              { "$divide": [{ "$subtract": ["$$currVal", "$$preVal"] }, "$$preVal"] },
                                              100
                                            ]
                                          },
                                          2
                                        ]
                                      },
                                      {
                                        "$round": [
                                          {
                                            "$multiply": [
                                              { "$divide": [{ "$subtract": ["$$currVal", "$$preVal"] }, "$$preVal"] },
                                              100
                                            ]
                                          },
                                          1
                                        ]
                                      }
                                    ]
                                  }
                                ]
                              }
                      ]
                    }
                  }
                }
            }
          }
        }
      }
    }
  }

def create_comparison_data():
    return {
  "$addFields": {
    "data": {
      "$arrayToObject": {
        "$map": {
          "input": { "$objectToArray": "$curr" },
          "as": "kv",
          "in": {
            "k": "$$kv.k",
            "v": {
              "$let": {
                "vars": {
                  "currVal": "$$kv.v",
                  "preVal": { "$getField": { "field": "$$kv.k", "input": "$pre" } },
                  "growthVal": { "$getField": { "field": "$$kv.k", "input": "$growth" } }
                },
                "in": {
                  "curr": "$$currVal.rawvalue",
                  "pre": "$$preVal.rawvalue",
                  "growth": {
                    "$cond": [
                      { "$in": ["$$kv.k", percent_fields] },
                      "$$growthVal",
                      { "$round": ["$$growthVal", 1] }
                    ]
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}


