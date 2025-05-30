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
end = alp.clock() - timedelta(days=1)
start = (end - timedelta(days=365.25*years))

alpaca_tickers = pd.DataFrame(alp.assets())

market.connect()
market.drop("index")
market.store("index",alpaca_tickers)
market.disconnect()

market.connect()
index = market.retrieve("index")
market.drop("prices")
tickers = list(index["ticker"].unique())
batchs = [tickers[i:i + 5] for i in range(0, len(tickers), 5)]
for batch in tqdm(batchs):
    try:
        tickers_data = alp.prices_bulk(batch,start,end)
        tickers_data = p.lower_column(tickers_data)
        tickers_data = p.utc_date(tickers_data)
        market.store("prices",tickers_data)
    except Exception as e:
        print(str(e))
market.create_index("prices","ticker")
market.disconnect()