## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from common.database.adatabase import ADatabase
from common.extractor.coinbase_extractor import CoinbaseExtractor  
from common.extractor.alpaca_extractor import AlpacaExtractor
from common.processor.utils import Utils
from time import sleep
import pandas as pd
ori = ADatabase("ori")
coin = CoinbaseExtractor()
alp = AlpacaExtractor(paper=False)

alp = AlpacaExtractor(paper=False)
end = pd.to_datetime(alp.clock()["date"])
ori.cloud_connect()
top = ori.retrieve("crypto_results").to_dict("records")[0]
ori.disconnect()

# # closing

if end.hour == 13:
    portfolio_uuid = coin.client.get_portfolios("DEFAULT")["portfolios"][0]["uuid"]
    portfolio = coin.client.get_portfolio_breakdown(portfolio_uuid)
    accounts = coin.client.get_accounts()
    orders = coin.client.list_orders(order_status="OPEN")["orders"]
    for order in orders:
        coin.client.cancel_orders([order.order_id for order in orders])