from dzgroshared.db.enums import Region, AMSDataSet
from pydantic import BaseModel, model_validator
from pydantic.json_schema import SkipJsonSchema


class CreateStreamSubscriptionRequest(BaseModel):
    clientRequestToken: str
    dataSetId: AMSDataSet
    region: Region|SkipJsonSchema[None]=None
    queueARN: str|SkipJsonSchema[None]=None

    @model_validator(mode="after")
    def setQueueArn(self):
        self.clientRequestToken = f'{self.clientRequestToken}-{self.dataSetId.value}'[:36]
        if self.region:
            region = "eu-west-1" if self.region == Region.EU else "us-east-1" if self.region == Region.NA else "us-west-2"
            self.queueARN = f"arn:aws:sqs:{region}:522814698847:ams"
        return self

class CreateStreamSubscriptionResponse(BaseModel):
    subscriptionId: str
    clientRequestToken: str

class ListStreamSubscriptionsRequest(BaseModel):
    maxResults: int = 5000
    startingToken: str|SkipJsonSchema[None] = None

class Destination(BaseModel):
    firehoseDestination: dict | SkipJsonSchema[None] = None
    sqsDestination: dict | SkipJsonSchema[None] = None

class StreamSubscription(BaseModel):
    createdDate: str
    notes: str | SkipJsonSchema[None] = None
    dataSetId: str
    destinationArn: str | SkipJsonSchema[None] = None
    destination: Destination | SkipJsonSchema[None] = None
    updatedDate: str
    subscriptionId: str
    status: str

class ListStreamSubscriptionsResponse(BaseModel):
    subscriptions: list[StreamSubscription]
    nextToken: str | SkipJsonSchema[None] = None

class GetStreamSubscriptionResponse(BaseModel):
    subscription: StreamSubscription

class UpdateStreamSubscriptionResponse(BaseModel):
    # Usually returns the updated subscription or status
    code: str
    message: str
    