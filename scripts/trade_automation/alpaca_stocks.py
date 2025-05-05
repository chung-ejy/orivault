## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from common.database.adatabase import ADatabase
from common.processor.processor import Processor as p
from common.extractor.alpaca_extractor import ALPClientExtractor  
from financial_common.portfolio_management.portfolio import Portfolio
from financial_common.risk.risk_type import RiskType
from financial_common.indicator.indicator import Indicator
import pandas as pd
from datetime import datetime, timedelta
from time import sleep
paper = False
orivault = ADatabase("ori")
market = ADatabase("market")
alp = ALPClientExtractor(paper=paper)

orivault.cloud_connect()
a = orivault.retrieve("results")
orivault.disconnect()
valid = a[(a["position_type"]=="long") & (a["timeframe"]=="week") & (a["selection_type"]!="long_short")].sort_values("pnl",ascending=False).head(20)
top = valid.head(1).to_dict(orient="records")[0]
pm = Portfolio(timeframe=top["timeframe"], ranking_metric=top["ranking_metric"], position_type=top["position_type"], grouping_type=top["grouping_type"].lower(), selection_type=top["selection_type"], allocation_type=top["allocation_type"], risk_type=top["risk_type"], selection_percentage=top["selection_percentage"])
print(pm.to_dict())

market.cloud_connect()
index = market.retrieve("ticker_overview")
market.disconnect()
sic_codes = pd.read_csv("./csv_files/sic_codes.csv").rename(columns={"SIC Code":"sic_code","Office":"office"}).dropna()
print(sic_codes.head())
index["sic_code"] = index["sic_code"].fillna(0).astype(int)
sic_codes["sic_code"] = sic_codes["sic_code"].fillna(0).astype(int)
index = index.merge(sic_codes[["sic_code","office"]],on="sic_code")



end = alp.clock()["date"] - timedelta(days=1)
start = (end - timedelta(days=200))

prices = []
for ticker in index["ticker"][:10]: 
    try:
        price = alp.prices(ticker,start,end)
        if price.index.size > 150:
            price = p.lower_column(price)
            price = p.utc_date(price)
        
            price.sort_values("date", inplace=True)
            price = p.additional_date_columns(price)
            for member in Indicator:
                price = member.calculate(price)
            for member in RiskType:
                price = member.apply(price)
            prices.append(price)
        sleep(0.35)
    except Exception as e:
        print(str(e))
        continue

simulation = pd.concat(prices).merge(index[["ticker","name","market_cap","office","sic_description"]],on="ticker",how="left")
simulation["market_cap"] = simulation["market_cap"].astype(float)
simulation["asset_class"] = "common_stock"
simulation.sort_values("date", inplace=True)

recommendations = pm.trades(simulation.copy())
print(recommendations)
# end = alp.clock()["date"]
# account = alp.account()
# cash = round(float(account["cash"]),2)
# chung.cloud_connect()
# recommendations = chung.retrieve("sar")
# chung.disconnect()
# todays_stuff = recommendations[recommendations["recommendation_date"]==recommendations["recommendation_date"].max()]
# positions = todays_stuff.index.size
# allocation = round(float(cash/positions),2)

# if end.weekday() == 0:
#     for row in todays_stuff.iterrows():
#         ticker = str(row[1]["ticker"])
#         direction = int(row[1]["direction"])
#         asset_info = alp.asset_info(ticker)
#         ticker_data = alp.latest_bar(ticker)
#         adjclose = float(ticker_data["c"])
#         qty = int(allocation/adjclose)
#         if bool(asset_info["tradable"]) == False:
#             continue
#         else:
#             if bool(asset_info["fractionable"]) == True:
#                 if direction == 1:
#                     print(alp.buy_fraction(ticker,allocation))
#                 elif direction == -1:
#                     print(alp.sell(ticker,allocation))
#                 else:
#                     print("invalid direction")
#             else:
#                 if direction == 1:
#                     print(alp.buy(ticker,qty))
#                 elif direction == -1:
#                     print(alp.sell(ticker,allocation))
#                 else:
#                     print("invalid direction")
# elif end.weekday() == 4:
#     alp.close()
# else:
#     print("resting",end.weekday())
