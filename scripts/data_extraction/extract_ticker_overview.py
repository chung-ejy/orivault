## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from common.extractor.alpaca_extractor import AlpacaExtractor
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

alp = AlpacaExtractor()
market = ADatabase("market")
poly = PolygonExtractor()
ticker_overviews = []

alpaca_tickers = pd.DataFrame(alp.assets()).rename(columns={"symbol":"ticker"})
relevant_tickers = alpaca_tickers[(alpaca_tickers["tradable"]==True) & (~alpaca_tickers["exchange"].isin(["OTC","CRYPTO"]))].copy()[["ticker","fractionable","exchange"]]
index = relevant_tickers.copy()

market.connect()
market.drop("index")
market.store("index",index)
market.disconnect()