## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from common.database.adatabase import ADatabase
from common.extractor.alpaca_extractor import AlpacaExtractor  

paper = False
orivault = ADatabase("ori")
alp = AlpacaExtractor(paper=paper)

end = alp.clock()["date"]
account = alp.account()
cash = round(float(account["cash"]),2)
orivault.cloud_connect()
recommendations = orivault.retrieve("recommendations")
results = orivault.retrieve("results").to_dict("records")[0]
orivault.disconnect()

if end.weekday() == 0:
    for row in recommendations.iterrows():
        ticker = str(row[1]["ticker"])
        direction = int(row[1]["position_type"])
        asset_info = alp.asset_info(ticker)
        ticker_data = alp.latest_bar(ticker)
        adjclose = float(ticker_data["c"])
        allocation = round(cash*row[1]["weight"],2) - 0.01 if results["allocation_type"] != "equal" else round(cash/recommendations.index.size,2) - 0.01
        qty = int(allocation/adjclose)
        if bool(asset_info["tradable"]) == False:
            continue
        else:
            if bool(asset_info["fractionable"]) == True:
                if direction == 1:
                    print(alp.buy_fraction(ticker,allocation))
                elif direction == -1:
                    print(alp.sell(ticker,allocation))
                else:
                    print("invalid direction")
            else:
                if direction == 1:
                    print(alp.buy(ticker,qty))
                elif direction == -1:
                    print(alp.sell(ticker,allocation))
                else:
                    print("invalid direction")
elif end.weekday() == 4:
    alp.close()
else:
    print("resting",end.weekday())
