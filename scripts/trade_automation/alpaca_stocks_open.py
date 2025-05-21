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
orivault.disconnect()
pm = Portfolio.from_dict(top)

if end.hour == 15: ## open positions
    account = alp.account()
    cash = round(float(account["cash"]),2)
    orivault.cloud_connect()
    recommendations = orivault.retrieve("recommendations")
    orivault.disconnect()
    for row in recommendations.iterrows():
        ticker = str(row[1]["ticker"])
        direction = int(row[1]["position_type"])
        ticker_data = alp.latest_bar(ticker)
        adjclose = round(float(ticker_data["c"]),2)
        allocation = round(cash*row[1]["weight"],2) - 0.01 if top["allocation_type"] != "equal" else round(cash/recommendations.index.size,2) - 0.01
        qty = int(allocation/adjclose)
        if direction == 1:
            print(alp.buy(ticker,adjclose,qty))
        elif direction == -1:
            print(alp.sell(ticker,adjclose,qty))
        else:
            print("invalid direction")
