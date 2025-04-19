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

index = pd.read_html("https://coinmarketcap.com/")[0][["Name","Market Cap"]]
index["industry"] = "crypto"
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

market.connect()
market.drop("cryptocurrencies")
market.store("cryptocurrencies",index[["ticker","market_cap","industry"]])
market.drop("crypto")
tickers = list(index["ticker"].unique())
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