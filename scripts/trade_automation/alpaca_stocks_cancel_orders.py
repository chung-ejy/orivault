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
from time import sleep

paper = False
orivault = ADatabase("ori")
alp = AlpacaExtractor(paper=paper)

end = pd.to_datetime(alp.clock()["date"])

orivault.cloud_connect()
top = orivault.retrieve("results").to_dict("records")[0]
recs = orivault.retrieve("recommendations")
orivault.disconnect()
pm = Portfolio.from_dict(top)

if end.weekday() <= 4 and end.hour ==  13:
    alp.cancel_orders()