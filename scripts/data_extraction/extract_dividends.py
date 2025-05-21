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
index = market.retrieve("index")
market.drop("dividends")

tickers = list(index["ticker"].unique())
batchs = [tickers[i:i + 4] for i in range(0, len(tickers), 4)]
for batch in tqdm(batchs):
    try:
        tickers_data = alp.dividends(batch,start,end).rename(columns={"symbol":"ticker","record_date":"date"})[["date","rate","ticker"]]
        tickers_data = p.lower_column(tickers_data)
        tickers_data = p.utc_date(tickers_data)
        market.store("dividends",tickers_data)
        sleep(0.35)
    except Exception as e:
        print(str(e))
market.create_index("dividends","ticker")
market.disconnect()

