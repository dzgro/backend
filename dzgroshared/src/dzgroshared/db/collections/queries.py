from datetime import datetime, timedelta
from bson import ObjectId
from dzgroshared.models.collections.queries import Query
from dzgroshared.models.enums import CollectionType, CollateTypeTag
from dzgroshared.db.DbUtils import DbManager
from dzgroshared.client import DzgroSharedClient

class QueryHelper:
    client: DzgroSharedClient
    db: DbManager
    marketplace: ObjectId
    uid: str

    def __init__(self, client: DzgroSharedClient, uid: str, marketplace: ObjectId) -> None:
        self.uid = uid
        self.client = client
        self.marketplace = marketplace
        self.db = DbManager(client.db.database.get_collection(CollectionType.QUERIES))

    def __get_month_datetimes_till(self, date_input: datetime) -> list[datetime]:
        first_day = date_input.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        delta = date_input.date() - first_day.date()
        return [first_day + timedelta(days=i) for i in range(delta.days + 1)]
    
    def __get_prev_month_datetimes_till_same_day(self, date_input: datetime) -> list[datetime]:
        last_day_prev_month = date_input.replace(day=1) - timedelta(days=1)
        day_limit = min(date_input.day, last_day_prev_month.day)
        start_day = last_day_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return [start_day + timedelta(days=i) for i in range(day_limit)]
    
    def __get_all_dates_of_prev_month(self, date_input: datetime) -> list[datetime]:
        last_day_prev_month = date_input.replace(day=1) - timedelta(days=1)
        first_day_prev_month = last_day_prev_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        days_in_month = last_day_prev_month.day
        return [first_day_prev_month + timedelta(days=i) for i in range(days_in_month)]
    
    async def getQueries(self):
        marketplace = await self.client.db.marketplaces.getMarketplace(self.marketplace)
        if not marketplace.enddate: raise ValueError("Marketplace is not active")
        endDate = marketplace.enddate
        data = await self.db.aggregate([{ '$match': { '$expr': { '$or': [ { '$eq': [ { '$ifNull': [ '$marketplace', None ] }, None ] }, { '$eq': [ '$marketplace', self.marketplace ] } ] } } }])
        queries: list[Query] = []
        for item in data:
            if item['tag']==CollateTypeTag.DAYS_7.value:
                queries.append(Query(**{**item, "curr": {"start": endDate-timedelta(days=6), "end": endDate},
                                     "pre": {"start": endDate-timedelta(days=13), "end": endDate-timedelta(days=7)}}))
            elif item['tag']==CollateTypeTag.DAYS_30:
                queries.append(Query(**{**item, "curr": {"start": endDate-timedelta(days=29), "end": endDate},
                                     "pre": {"start": endDate-timedelta(days=39), "end": endDate-timedelta(days=30)}}))
            elif item['tag']==CollateTypeTag.MONTH_ON_NONTH.value:
                currdates = self.__get_month_datetimes_till(endDate)
                preDates = self.__get_prev_month_datetimes_till_same_day(endDate)
                queries.append(Query(**{**item, "curr": {"start": currdates[0], "end": currdates[-1]},
                                     "pre": {"start": preDates[0], "end": preDates[-1]}}))
            elif item['tag']==CollateTypeTag.MONTH_OVER_MONTH.value:
                currdates = self.__get_month_datetimes_till(endDate)
                preDates = self.__get_all_dates_of_prev_month(endDate)
                queries.append(Query(**{**item, "curr": {"start": currdates[0], "end": currdates[-1]},
                                     "pre": {"start": preDates[0], "end": preDates[-1]}}))
            else: queries.append(Query(**item))
        return queries

