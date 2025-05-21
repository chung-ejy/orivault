## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

## Bespoke class imports
from common.database.adatabase import ADatabase
from common.processor.processor import Processor as p
from common.extractor.coinbase_extractor import CoinbaseExtractor
from common.extractor.alpaca_extractor import AlpacaExtractor
from financial_common.indicator.indicator import Indicator
from financial_common.metric.metric import Metric
from financial_common.risk.risk_type import RiskType
from financial_common.portfolio_management.portfolio import Portfolio
from datetime import datetime, timedelta
import pandas as pd

market = ADatabase("market")
ori = ADatabase("ori")
coinbase = CoinbaseExtractor()
alp = AlpacaExtractor(paper=False)
## Retrieve existing stocks 
market.cloud_connect()
index = market.retrieve("cryptocurrencies")
market.disconnect()

ori.cloud_connect()
results = ori.retrieve("crypto_results")
ori.disconnect()

top = results.to_dict("records")[0]

pm = Portfolio.from_dict(top)
end = pd.to_datetime(alp.clock()["date"])
start = end - timedelta(days=200)


if end == 9:
    prices = []
    for ticker in index["ticker"]: 
        try:
            price = coinbase.prices(ticker,start,end)
            price["ticker"] = ticker
            price = p.lower_column(price)
            price["date"] = [datetime.fromtimestamp(int(x)) for x in price["start"]]
            price = p.utc_date(price)
            for col in price.columns:
                if col not in ["date", "ticker"]:
                    try:
                        price[col] = price[col].astype(float)
                    except Exception as e:
                        print(str(e))
                        continue
            price.rename(columns={"close":"adjclose"},inplace=True)
            price = p.lower_column(price)
            price = p.utc_date(price)
        
            price.sort_values("date", inplace=True)
            price = p.additional_date_columns(price)
            price = Metric.indicator_type_factory(top["grouping_type"].lower()).calculate(price,timeframe=pm.rolling_window,live=True)
            price = Indicator.indicator_type_factory(top["ranking_metric"].lower()).calculate(price,timeframe=pm.rolling_window,live=True)
            price = RiskType.risk_type_factory(top["risk_type"].lower()).apply(price,timeframe=pm.rolling_window)
            prices.append(price)
        except Exception as e:
            print(str(e))
            continue

    simulation = pd.concat(prices)
    simulation.sort_values("date", inplace=True)
    recs = pm.recs(simulation)

    ori.cloud_connect()
    ori.drop("crypto_recommendations")
    ori.store("crypto_recommendations",recs)
    ori.disconnect()