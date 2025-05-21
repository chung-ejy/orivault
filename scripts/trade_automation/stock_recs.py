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
end = pd.to_datetime(alp.clock()["date"])

orivault.cloud_connect()
a = orivault.retrieve("results")
orivault.disconnect()
top = a.head(1).to_dict(orient="records")[0]

pm = Portfolio.from_dict(top)

market.cloud_connect()
index = market.retrieve("ticker_overview")
market.disconnect()

if end.hour == 9:
    rolling_window = top["rolling_window"]
    delta_days = rolling_window/5*7*2
    tickers_per_batch = int(len(index["ticker"].unique())/rolling_window/5)
    end = alp.clock()["date"] - timedelta(days=1)
    start = (end - timedelta(days=delta_days))
    prices = []
    tickers = list(index["ticker"].unique())
    batchs = [tickers[i:i + tickers_per_batch] for i in range(0, len(tickers), tickers_per_batch)]
    for batch in batchs:
        tickers_data = alp.prices_bulk(batch,start,end)
        sleep(0.35)
        for ticker in batch:
            try:
                price = tickers_data[tickers_data["ticker"] == ticker].copy()
                price = p.lower_column(price)
                price = p.utc_date(price)
                price.sort_values("date", inplace=True)
                price = p.additional_date_columns(price)
                price = Metric.indicator_type_factory(top["grouping_type"].lower()).calculate(price,timeframe=rolling_window,live=True)
                price = Indicator.indicator_type_factory(top["ranking_metric"].lower()).calculate(price,timeframe=rolling_window,live=True)
                price = RiskType.risk_type_factory(top["risk_type"].lower()).apply(price)
                prices.append(price)
            except Exception as e:
                print(str(e))

    simulation = pd.concat(prices)
    simulation.sort_values("date", inplace=True)
    trades = pm.recs(simulation.copy()).sort_values("group_percentile", ascending=False)

    orivault.cloud_connect()
    orivault.drop("recommendations")
    orivault.store("recommendations",trades)
    orivault.disconnect()