from amazonapi.adapi.common.ams import CreateStreamSubscriptionRequest, ListStreamSubscriptionsRequest
from dzgrosecrets import SecretManager
from db import DbClient
from bson import ObjectId
from models.enums import AMSDataSet, AmazonAccountType
from models.amazonapi.model import AmazonApiObject

secrets = SecretManager()
MONGOURI = secrets.MONGO_DB_CONNECT_URI
dbClient = DbClient(MONGOURI)

marketplaceId = ObjectId("6895638c452dc4315750e826")
uid= "41e34d1a-6031-70d2-9ff3-d1a704240921"

async def subscribe():
    obj = AmazonApiObject(** await dbClient.marketplaces(uid).getMarketplaceApiObject(marketplaceId, secrets.ADS_CLIENT_ID, secrets.ADS_CLIENT_SECRET, AmazonAccountType.ADVERTISING))
    from amazonapi import AmazonApiClient
    ams = AmazonApiClient(obj).ad.common.amsClient
    req = CreateStreamSubscriptionRequest(
        clientRequestToken=str(marketplaceId),
        dataSetId=AMSDataSet.SP_CONVERSIONS,
        region=obj.region
    )
    res = await ams.createStreamSubscription(req)
    # res = await ams.listStreamSubscription(ListStreamSubscriptionsRequest())
    # res = await ams.updateStreamSubscription("amzn1.fead.cs1.gLo5pPPOhL6glLdrkopCZw")
    print(res.model_dump(exclude_none=True, by_alias=True))

import asyncio
asyncio.run(subscribe())

# 'amzn1.fead.cs1.pPWM48rKPssUBnsqpblFXg'
# 62c911f4-d5aa-5442-8979-70e023567a94
# 'amzn1.fead.cs1.pI9GrBURu1HMdCe0RrFGOg'
# amzn1.fead.cs1.gLo5pPPOhL6glLdrkopCZw