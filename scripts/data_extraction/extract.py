## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from datetime import datetime, timedelta
from common.processor.processor import Processor as p
from common.database.adatabase import ADatabase
from common.extractor.alpaca_extractor import AlpacaExtractor
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
alp = AlpacaExtractor()

## Download stock prices
end = alp.clock()["date"] - timedelta(days=1)
start = (end - timedelta(days=365.25*years))

market.connect()
index = market.retrieve("ticker_overview")
market.drop("prices")

tickers = list(index["ticker"].unique())
batchs = [tickers[i:i + 7] for i in range(0, len(tickers), 7)]
for batch in tqdm(batchs):
    tickers_data = alp.prices_bulk(batch,start,end)
    sleep(0.35)
    for ticker in batch:
        try:
            ticker_data = tickers_data[tickers_data["ticker"] == ticker].copy()
            ticker_data["ticker"] = ticker
            ticker_data = p.lower_column(ticker_data)
            ticker_data = p.utc_date(ticker_data)
            market.store("prices",ticker_data)
        except Exception as e:
            print(str(e))
market.create_index("prices","ticker")
market.disconnect()