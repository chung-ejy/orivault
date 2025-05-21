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

tickers = pd.DataFrame([x.__dict__ for x in coinbase.client.get_accounts()["accounts"] if x.currency != "USD" and x.currency != "USDT"])
tickers = tickers[["name","currency","active"]][tickers["active"]==True]
tickers["ticker"] = tickers["currency"] + "-USD"

alpaca_tickers = pd.DataFrame(alp.assets()).rename(columns={"symbol":"ticker"})
relevant_tickers = alpaca_tickers[(alpaca_tickers["tradable"]==True) & (~alpaca_tickers["exchange"].isin(["OTC","CRYPTO"]))].copy()[["ticker","fractionable","exchange"]]

market.cloud_connect()
market.drop("ticker_overview")
market.store("ticker_overview",relevant_tickers)
market.disconnect()

market.cloud_connect()
market.drop("cryptocurrencies")
market.store("cryptocurrencies",tickers)
market.disconnect()
