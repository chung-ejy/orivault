## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from common.database.adatabase import ADatabase
from common.processor.processor import Processor as p
from common.extractor.alpaca_extractor import AlpacaExtractor  
from financial_common.portfolio_management.portfolio import Portfolio
from financial_common.risk.risk_type import RiskType
from financial_common.indicator.indicator import Indicator
from financial_common.metric.metric import Metric
import pandas as pd
from datetime import datetime, timedelta
from time import sleep
paper = False
orivault = ADatabase("ori")
market = ADatabase("market")
alp = AlpacaExtractor(paper=paper)

if datetime.now().weekday() == 0: # Monday
    orivault.cloud_connect()
    a = orivault.retrieve("results")
    orivault.disconnect()
    top = a.head(1).to_dict(orient="records")[0]
    pm = Portfolio(timeframe=top["timeframe"].lower(), ranking_metric=top["ranking_metric"], 
                   position_type=top["position_type"], grouping_type=top["grouping_type"].lower(), 
                   selection_type=top["selection_type"], allocation_type=top["allocation_type"], 
                   risk_type=top["risk_type"], selection_percentage=top["selection_percentage"])
    rolling_window = top["rolling_window"]
    market.cloud_connect()
    index = market.retrieve("ticker_overview")
    market.disconnect()

    end = alp.clock()["date"] - timedelta(days=1)
    start = (end - timedelta(days=200))

    prices = []
    for ticker in index["ticker"]: 
        try:
            price = alp.prices(ticker,start,end)
            price = p.lower_column(price)
            price = p.utc_date(price)
            price.sort_values("date", inplace=True)
            price = p.additional_date_columns(price)
            for member in Metric:
                price = member.calculate(price,timeframe=rolling_window,live=True)
            for member in Indicator:
                price = member.calculate(price,timeframe=rolling_window,live=True)
            for member in RiskType:
                price = member.apply(price)
            prices.append(price)
            sleep(0.35)
        except Exception as e:
            print(str(e))
            continue

    simulation = pd.concat(prices)
    simulation.sort_values("date", inplace=True)
    trades = pm.recs(simulation.copy())

    orivault.cloud_connect()
    orivault.drop("recommendations")
    orivault.store("recommendations",trades)
    orivault.disconnect()