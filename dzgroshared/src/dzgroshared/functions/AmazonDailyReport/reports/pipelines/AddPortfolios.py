import asyncio
from dzgroshared.amazonapi import AdApiClient
from dzgroshared.models.amazonapi.errors import APIError
from dzgroshared.models.amazonapi.adapi.common.portfolios import ListPortfoliosRequestContent, Portfolio
from dzgroshared.models.enums import AdAssetType
from dzgroshared.models.extras.amazon_daily_report import MarketplaceObjectForReport


class PortfolioProcessor:
    marketplace: MarketplaceObjectForReport
    adapi: AdApiClient
    def __init__(self, marketplace: MarketplaceObjectForReport, adapi: AdApiClient) -> None:
        self.marketplace = marketplace
        self.adapi = adapi

    
    async def getPortfolios(self):
        res = await self.__getPortfolioBatch(None)
        portfolios = res.portfolios
        while res.nextToken is not None:
            res = await self.__getPortfolioBatch(res.nextToken)
            portfolios.extend(res.portfolios)
        return self._formatPortfolios(portfolios)

    async def __getPortfolioBatch(self, token:str|None):
        try:
            return await self.adapi.common.portfoliosClient.list_portfolios(ListPortfoliosRequestContent(nextToken=token))
        except APIError as e:
            if e.status_code == 429:
                await asyncio.sleep(5)
                return self.__getPortfolioBatch(token)
            raise e

    def _formatPortfolios(self, portfolios: list[Portfolio]):
        formatted: list[dict] = []
        for p in portfolios:
            x = p.model_dump(exclude_none=True, by_alias=True)
            x['_id'] = f'{str(self.marketplace.id)}_{p.portfolioId}'
            x['id'] = p.portfolioId
            x['assettype'] = AdAssetType.PORTFOLIO.value
            del x['portfolioId']
            formatted.append(x)
        return formatted
