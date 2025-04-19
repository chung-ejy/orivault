## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from datetime import datetime, timedelta
from common.processor.processor import Processor as p
from common.database.adatabase import ADatabase
from common.extractor.polygon_extractor import PolygonExtractor
from dotenv import load_dotenv
from time import sleep
from tqdm import tqdm
import requests as r
import pandas as pd
import os
load_dotenv()

market = ADatabase("market")
poly = PolygonExtractor()
ticker_overviews = []

## Download current stocks
ticker_info = poly.ticker_info()
ticker_infos = []
ticker_infos.extend(ticker_info["results"])
key = os.getenv("POLYGONKEY")
for i in range(20):
    try:
        if "next_url" in ticker_info:
            next_url = ticker_info["next_url"]
        else:
            break
        ticker_info = r.get(next_url+f"&apiKey={key}").json()
        ticker_infos.extend(ticker_info["results"])
        sleep(20)
    except Exception as e:
        print(str(e))
index = pd.DataFrame(ticker_infos).sort_values("ticker")
prices = []

market.connect()
market.drop("index")
market.store("index",index)
market.disconnect()

market.connect()
market.drop("ticker_overview")
tickers = list(index["ticker"].unique())
for ticker in tqdm(tickers):
    try:
        ticker_data = poly.ticker_overview(ticker)["results"]
        market.store("ticker_overview",pd.DataFrame([ticker_data]))
        sleep(12)
    except Exception as e:
        print(str(e))
market.disconnect()