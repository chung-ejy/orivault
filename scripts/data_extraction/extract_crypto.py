## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from datetime import datetime, timedelta
from common.processor.processor import Processor as p
from common.database.adatabase import ADatabase
from common.extractor.coinbase_extractor import CoinbaseExtractor
from dotenv import load_dotenv
import pandas as pd
import os
import re
load_dotenv()

## Initialize classes and constants
market = ADatabase("market")
coinbase = CoinbaseExtractor()

## Download stock prices
end = datetime.now()
start = (datetime.now() - timedelta(days=350))

tickers = pd.DataFrame([x.__dict__ for x in coinbase.client.get_accounts()["accounts"] if x.currency != "USD" and x.currency != "USDT"])
tickers = tickers[["name","currency","active"]][tickers["active"]==True]
tickers["ticker"] = tickers["currency"] + "-USD"
market.connect()
market.drop("cryptocurrencies")
market.store("cryptocurrencies",tickers)
tickers = list(tickers["ticker"].unique())
for ticker in tickers:
    try:
        ticker_data = coinbase.prices(ticker,start,end)
        ticker_data["ticker"] = ticker
        ticker_data = p.lower_column(ticker_data)
        ticker_data["date"] = [datetime.fromtimestamp(int(x)) for x in ticker_data["start"]]
        ticker_data = p.utc_date(ticker_data)
        market.store("crypto",ticker_data)
    except Exception as e:
        print(str(e))
market.create_index("crypto","ticker")
market.disconnect()