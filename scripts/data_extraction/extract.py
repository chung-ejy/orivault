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
from common.extractor.tiingo_extractor import TiingoExtractor
from dotenv import load_dotenv
from time import sleep
from tqdm import tqdm
import requests as r
import pandas as pd
import os
load_dotenv()

## Initialize classes and constants
years = 15
market = ADatabase("market")
poly = PolygonExtractor()
tiingo = TiingoExtractor()

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