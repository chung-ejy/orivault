## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from common.database.adatabase import ADatabase
from common.extractor.alpaca_extractor import AlpacaExtractor  
from financial_common.portfolio_management.portfolio import Portfolio
import pandas as pd
paper = False
orivault = ADatabase("ori")
alp = AlpacaExtractor(paper=paper)

end = pd.to_datetime(alp.clock()["date"])

orivault.cloud_connect()
top = orivault.retrieve("results").to_dict("records")[0]
recs = orivault.retrieve("recommendations")
orivault.disconnect()
pm = Portfolio.from_dict(top)

if end.hour == 15: ## close positions
    positions = alp.positions()
    alp.cancel_orders()
    for row in positions.iterrows():
        position = row[1]
        ticker = str(position["symbol"])
        ticker_data = alp.latest_bar(ticker)
        adjclose = round(float(ticker_data["c"]),2)
        side = str(position["side"])
        qty = int(position["qty_available"])
        if side == "long":
            print(alp.sell(ticker,adjclose,qty))
        else:
            print(alp.buy(ticker,adjclose,qty))