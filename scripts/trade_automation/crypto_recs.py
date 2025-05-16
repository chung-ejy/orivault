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
from financial_common.indicator.indicator import Indicator
from financial_common.metric.metric import Metric
from financial_common.risk.risk_type import RiskType
from financial_common.portfolio_management.portfolio import Portfolio
from datetime import datetime, timedelta
import pandas as pd

if datetime.now().weekday() == 0:
    market = ADatabase("market")
    ori = ADatabase("ori")
    coinbase = CoinbaseExtractor()
    ## Retrieve existing stocks 
    market.cloud_connect()
    index = market.retrieve("cryptocurrencies")
    market.disconnect()

    ori.cloud_connect()
    results = ori.retrieve("crypto_results")
    ori.disconnect()

    end = datetime.now()
    start = end - timedelta(days=200)

    available_assets = coinbase.listed_crypto()
    index = index[index["ticker"].isin(available_assets)]

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
            for member in Metric:
                price = member.calculate(price,live=True,timeframe=20)
            for member in Indicator:
                price = member.calculate(price,live=True,timeframe=20)
            for member in RiskType:
                price = member.apply(price)
            prices.append(price)
        except Exception as e:
            print(str(e))
            continue

    simulation = pd.concat(prices)
    simulation.sort_values("date", inplace=True)

    top = results[results["timeframe"]=="WEEK"].sort_values("pnl",ascending=False).to_dict("records")[0]
    pm = Portfolio(timeframe=top["timeframe"].lower(), ranking_metric=top["ranking_metric"], position_type=top["position_type"], grouping_type=top["grouping_type"].lower(), selection_type=top["selection_type"], allocation_type=top["allocation_type"], risk_type=top["risk_type"], selection_percentage=top["selection_percentage"])
    recs = pm.recs(simulation)

    ori.cloud_connect()
    ori.drop("crypto_recommendations")
    ori.store("crypto_recommendations",recs)
    ori.disconnect()