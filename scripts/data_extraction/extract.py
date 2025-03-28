import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
from common.processor.processor import Processor as p
from common.database.adatabase import ADatabase
from time import sleep
from common.extractor.polygon_extractor import PolygonExtractor
from common.extractor.tiingo_extractor import TiingoExtractor
import requests as r
from dotenv import load_dotenv
load_dotenv()
import os
from time import sleep

years = 5
market = ADatabase("market")
poly = PolygonExtractor(os.getenv("POLYGONKEY"))
tiingo = TiingoExtractor()
ticker_info = poly.ticker_info()
ticker_infos = []
ticker_infos.extend(ticker_info["results"])
key = os.getenv("POLYGONKEY")
for i in range(6):
    try:
        ticker_info = r.get(ticker_info["next_url"]+f"&apiKey={key}").json()
        ticker_infos.extend(ticker_info["results"])
        sleep(20)
    except Exception as e:
        print(str(e))
index = pd.DataFrame(ticker_infos).sort_values("ticker")
prices = []

end = datetime.now()
start = (datetime.now() - timedelta(days=365.25*years))
market.connect()
market.drop("index")
market.drop("prices")
tickers = list(index["ticker"].unique())
market.store("index",index)
for ticker in tqdm(tickers):
    try:
        ticker_data = tiingo.prices(ticker,start,end)
        ticker_data["ticker"] = ticker
        market.store("prices",p.column_date_processing(ticker_data))
    except Exception as e:
        print(str(e))
market.create_index("prices","ticker")
market.disconnect()