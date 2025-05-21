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

if end.hour == 8: ## handle stoplosses
    positions = alp.positions()
    for row in positions.iterrows():
        position = row[1]
        ticker = str(position["symbol"])
        price = float(position["avg_entry_price"])
        side = str(position["side"])
        qty = int(position["qty_available"])
        if side == "long":
            stop_price = round(price * (1-pm.stoploss),2)
            print(alp.long_stop_loss(ticker,stop_price,qty))
        else:
            stop_price = round(price * (1+pm.stoploss),2)
            print(alp.short_stop_loss(ticker,stop_price,qty))