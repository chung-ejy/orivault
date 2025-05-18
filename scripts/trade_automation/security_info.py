## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from common.processor.processor import Processor as p
from common.database.adatabase import ADatabase
from common.extractor.polygon_extractor import PolygonExtractor
from common.extractor.alpaca_extractor import AlpacaExtractor
from common.extractor.coinbase_extractor import CoinbaseExtractor
from dotenv import load_dotenv
from time import sleep
from tqdm import tqdm
from datetime import datetime
import requests as r
import re
import pandas as pd
import os
load_dotenv()

market = ADatabase("market")
poly = PolygonExtractor()
alp = AlpacaExtractor(paper=False)
coinbase = CoinbaseExtractor()
ticker_overviews = []
if datetime.now().weekday() == 6:
    alpaca_tickers = pd.DataFrame(alp.assets()).rename(columns={"symbol":"ticker"})
    relevant_tickers = alpaca_tickers[(alpaca_tickers["tradable"]==True) & (~alpaca_tickers["exchange"].isin(["OTC","CRYPTO"]))].copy()[["ticker","fractionable","exchange"]]

    market.cloud_connect()
    market.drop("ticker_overview")
    market.store("ticker_overview",relevant_tickers)
    market.disconnect()

    index = pd.read_html("https://coinmarketcap.com/")[0][["Name","Market Cap"]]
    def extract_ticker(s):
        match = re.search(r'[A-Z]+$', s)
        if match:
            # Remove repetitive patterns
            unique_sequence = re.match(r'(.+?)\1*$', match.group(0)).group(1)
            return unique_sequence + "-USD"
        return None

    # Apply the function to the "Name" column
    index['ticker'] = index['Name'].apply(extract_ticker)
    index["market_cap"] = [int(x.split("$")[2].replace(",","")) if type(x) == str else 550000000 for x in index["Market Cap"]]

    market.cloud_connect()
    market.drop("cryptocurrencies")
    market.store("cryptocurrencies",index[["ticker","market_cap"]])
    market.disconnect()
