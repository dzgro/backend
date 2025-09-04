revenue :dict = {"label": "Net Revenue", "key": "revenue", "desc": "Total value of orders after returns including tax"}
ordervalue :dict = {"label": "Gross Revenue", "key": "ordervalue", "desc": "Total value of purchases including tax"}
returnordervalue :dict = {"label": "Returned Revenue", "key": "returnordervalue", "desc": "Total value of returned purchases including tax"}
tacos :dict = {"label": "TACoS %", "key": "tacos", "desc": "Ad cost as a percentage of total revenue"}
organicsalespercent :dict = {"label": "Organic Sales %", "key": "organicsalespercent", "desc": "Percentage of revenue generated from non-ad sources"}
quantity :dict = {"label": "Quantity", "key": "quantity", "desc": "Total items purchased"}
returnquantity :dict = {"label": "Return Quantity", "key": "returnquantity", "desc": "Items returned by customers"}
netquantity :dict = {"label": "Net Quantity", "key": "netquantity", "desc": "Net items sold after returns"}
returnpercent :dict = {"label": "Return %", "key": "returnpercent", "desc": "Items returned as a percentage of total items sold"}
asp :dict = {"label": "Average Selling Price", "key": "asp", "desc": "Average selling price of items sold"}
expenses :dict = {"label": "Expenses", "key": "expenses", "desc": "Total Expenses"}
fees :dict = {"label": "Fees", "key": "fees", "desc": "Fees charged by the platform"}
otherexpenses :dict = {"label": "Other Expenses", "key": "otherexpenses", "desc": "Additional adjustments or costs"}
netproceeds :dict = {"label": "Net Payout", "key": "netproceeds", "desc": "Net revenue after fees, returns, and adjustments"}
netpayoutperunit :dict = {"label": "Net Payout/Unit", "key": "netpayoutperunit", "desc": "Average net revenue earned per item sold"}
netpayoutpercent :dict = {"label": "Net Payout %", "key": "netpayoutpercent", "desc": "Net revenue as a percentage of total order value"}
impressions :dict = {"label": "Impressions", "key": "impressions", "desc": "Total number of times ads were shown"}
clicks :dict = {"label": "Clicks", "key": "clicks", "desc": "Total number of times ads were clicked"}
ctr :dict = {"label": "CTR %", "key": "ctr", "desc": "Percentage of clicks received out of total impressions"}
cost :dict = {"label": "Ad Spend", "key": "cost", "desc": "Cost incurred for ads"}
cpc :dict = {"label": "CPC", "key": "cpc", "desc": "Average cost spent for each click"}
units :dict = {"label": "Ad Units", "key": "units", "desc": "Total number of items sold through ads"}
orders :dict = {"label": "Ad Orders", "key": "orders", "desc": "Total number of orders received through ads"}
cvr :dict = {"label": "CVR %", "key": "cvr", "desc": "Percentage of clicks that resulted in a purchase"}
sales :dict = {"label": "Ad Sales", "key": "sales", "desc": "Revenue generated from ads"}
acos :dict = {"label": "ACOS %", "key": "acos", "desc": "Cost spent on advertising as a percentage of revenue generated from ads"}
roas :dict = {"label": "ROAS", "key": "roas", "desc": "Revenue generated for every unit of ad cost"}
adspendperunit :dict = {"label": "Ad Spend/Unit", "key": "adspendperunit", "desc": "Average ad cost per item sold"}
buyboxviewpercent :dict = {"label": "Buy Box %", "key": "buyboxviewpercent", "desc": "% times the featured offer was with your brand"}
pageviews :dict = {"label": "Page Views", "key": "pageviews", "desc": "Total number of pages viewed"}
browserpageviews :dict = {"label": "Browser Page Views", "key": "browserpageviews", "desc": "Pages viewed from web browsers"}
browserpageviewpercent :dict = {"label": "Browser Page View %", "key": "browserpageviewpercent", "desc": "Browser page views as a percentage of total page views"}
mobileapppageviews :dict = {"label": "Mobile App Page Views", "key": "mobileapppageviews", "desc": "Pages viewed from mobile apps"}
mobileapppageviewpercent :dict = {"label": "Mobile App Page View %", "key": "mobileapppageviewpercent", "desc": "Mobile app page views as a percentage of total page views"}    
unitsessionpercent :dict = {"label": "Unit Session %", "key": "unitsessionpercent", "desc": "Percentage of sessions that resulted in a purchase"}
sessions :dict = {"label": "Sessions", "key": "sessions", "desc": "Total number of user sessions"}
browsersessions :dict = {"label": "Browser Sessions", "key": "browsersessions", "desc": "Sessions originating from web browsers"}
mobileappsessions :dict = {"label": "Mobile App Sessions", "key": "mobileappsessions", "desc": "Sessions originating from mobile applications"}
browsersessionpercent :dict = {"label": "Browser Session %", "key": "browsersessionpercent", "desc": "Browser sessions as a percentage of total sessions"}
mobileappsessionpercent :dict = {"label": "Mobile App Session %", "key": "mobileappsessionpercent", "desc": "Mobile app sessions as a percentage of total sessions"}

sales_fields = [
    {"label": "Net Revenue", "key": "revenue", "desc": "Total value of orders after returns including tax"},
    {"label": "Gross Revenue", "key": "ordervalue", "desc": "Total value of purchases including tax"},
    {"label": "Returned Revenue", "key": "returnordervalue", "desc": "Total value of returned purchases including tax"},
    {"label": "TACoS %", "key": "tacos", "desc": "Ad cost as a percentage of total revenue"},
    {"label": "Organic Sales %", "key": "organicsalespercent", "desc": "Percentage of revenue generated from non-ad sources"},
    {"label": "Quantity", "key": "quantity", "desc": "Total items purchased"},
    {"label": "Return Quantity", "key": "returnquantity", "desc": "Items returned by customers"},
    {"label": "Net Quantity", "key": "netquantity", "desc": "Net items sold after returns"},
    {"label": "Return %", "key": "returnpercent", "desc": "Items returned as a percentage of total items sold"},
    {"label": "Average Selling Price", "key": "asp", "desc": "Average selling price of items sold"},
    {"label": "Expenses", "key": "expenses", "desc": "Total Expenses"},
    {"label": "Fees", "key": "fees", "desc": "Fees charged by the platform"},
    {"label": "Other Expenses", "key": "otherexpenses", "desc": "Additional adjustments or costs"},
    {"label": "Net Payout", "key": "netproceeds", "desc": "Net revenue after fees, returns, and adjustments"},
    {"label": "Net Payout/Unit", "key": "netpayoutperunit", "desc": "Average net revenue earned per item sold"},
    {"label": "Net Payout %", "key": "netpayoutpercent", "desc": "Net revenue as a percentage of total order value"}
]

traffic_fields = [
    {"label": "Buy Box %", "key": "buyboxviewpercent", "desc": "% times the featured offer was with your brand"},
    {"label": "Page Views", "key": "pageviews", "desc": "Total number of pages viewed"},
    {"label": "Browser Page Views", "key": "browserpageviews", "desc": "Pages viewed from web browsers"},
    {"label": "Browser Page View %", "key": "browserpageviewpercent", "desc": "Browser page views as a percentage of total page views"},
    {"label": "Mobile App Page Views", "key": "mobileapppageviews", "desc": "Pages viewed from mobile apps"},
    {"label": "Mobile App Page View %", "key": "mobileapppageviewpercent", "desc": "Mobile app page views as a percentage of total page views"},
    {"label": "Unit Session %", "key": "unitsessionpercent", "desc": "Percentage of sessions that resulted in a purchase"},
    {"label": "Sessions", "key": "sessions", "desc": "Total number of user sessions"},
    {"label": "Browser Sessions", "key": "browsersessions", "desc": "Sessions originating from web browsers"},
    {"label": "Mobile App Sessions", "key": "mobileappsessions", "desc": "Sessions originating from mobile applications"},
    {"label": "Browser Session %", "key": "browsersessionpercent", "desc": "Browser sessions as a percentage of total sessions"},
    {"label": "Mobile App Session %", "key": "mobileappsessionpercent", "desc": "Mobile app sessions as a percentage of total sessions"},
]

ad_fields = [
    {"label": "Impressions", "key": "impressions", "desc": "Total number of times ads were shown"},
    {"label": "Clicks", "key": "clicks", "desc": "Total number of times ads were clicked"},
    {"label": "CTR %", "key": "ctr", "desc": "Percentage of clicks received out of total impressions"},
    {"label": "Ad Spend", "key": "cost", "desc": "Cost incurred for ads"},
    {"label": "CPC", "key": "cpc", "desc": "Average cost spent for each click"},
    {"label": "Ad Units", "key": "units", "desc": "Total number of items sold through ads"},
    {"label": "Ad Orders", "key": "orders", "desc": "Total number of items sold through ads"},
    {"label": "CVR %", "key": "cvr", "desc": "Percentage of clicks that resulted in a purchase"},
    {"label": "Ad Sales", "key": "sales", "desc": "Revenue generated from ads"},
    {"label": "ACOS %", "key": "acos", "desc": "Cost spent on advertising as a percentage of revenue generated from ads"},
    {"label": "ROAS", "key": "roas", "desc": "Revenue generated for every unit of ad cost"},
    {"label": "Ad Spend/Unit", "key": "adspendperunit", "desc": "Average ad cost per item sold"}
]

# import json
# for field in sales_fields+ad_fields+traffic_fields:
#     print(field['key'], ":dict =", json.dumps(field))

metricsGroups = [
    {
        "label": "Sales",
        "key": "sales",
        "items": [
            revenue.update({"items": [ordervalue, returnordervalue]}),
            tacos,
            organicsalespercent,
            quantity.update({"items": [returnquantity, netquantity, returnpercent]}),
            asp,
            expenses.update({"items": [fees, otherexpenses]}),
            netproceeds.update({"items": [netpayoutperunit, netpayoutpercent]})

        ]
    },
    {
        "label": "Advertisement",
        "key": "ad",
        "items": [
            impressions,
            clicks.update({"items": [ctr]}),
            cost.update({"items": [cpc]}),
            units.update({"items": [orders,cvr]}),
            sales.update({"items": [acos, adspendperunit]}),
            roas

        ]
    },
    {
        "label": "Traffic",
        "key": "traffic",
        "items": [
            sessions.update({"items": [browsersessions, browsersessionpercent, mobileappsessions, mobileappsessionpercent]}),
            unitsessionpercent,
            pageviews.update({"items": [browserpageviews, browserpageviewpercent, mobileapppageviews, mobileapppageviewpercent]}),
            buyboxviewpercent
        ]
    },
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
    return { "$addFields": {f"{data_key}.{key}": { "$ifNull": [f"${data_key}.{key}", 0] } for key in percent_fields+non_percent_fields} }

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


