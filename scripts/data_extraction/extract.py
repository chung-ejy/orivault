from datetime import datetime, timedelta
from common.processor.processor import Processor as p
from common.database.adatabase import ADatabase
from common.extractor.polygon_extractor import PolygonExtractor
from common.extractor.tiingo_extractor import TiingoExtractor
from dotenv import load_dotenv
from time import sleep
from tqdm import tqdm
import requests as r
import pandas as pd
import os
load_dotenv()

## Initialize classes and constants
years = 5
market = ADatabase("market")
poly = PolygonExtractor(os.getenv("POLYGONKEY"))
tiingo = TiingoExtractor()

## Download current stocks
ticker_info = poly.ticker_info()
ticker_infos = []
ticker_infos.extend(ticker_info["results"])
key = os.getenv("POLYGONKEY")
for i in range(6):
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

## Download stock prices
end = datetime.now()
start = (datetime.now() - timedelta(days=365.25*years))

market.connect()
market.drop("prices")
tickers = list(index["ticker"].unique())
for ticker in tqdm(tickers):
    try:
        ticker_data = tiingo.prices(ticker,start,end)
        ticker_data["ticker"] = ticker
        ticker_data = p.lower_column(ticker_data)
        ticker_data = p.utc_date(ticker_data)
        market.store("prices",ticker_data)
        sleep(1.2)
    except Exception as e:
        print(str(e))
market.create_index("prices","ticker")
market.disconnect()