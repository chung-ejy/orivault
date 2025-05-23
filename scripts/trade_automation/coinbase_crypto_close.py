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

if end.weekday <= 4 and end.hour ==  14:
    portfolio_uuid = coin.client.get_portfolios("DEFAULT")["portfolios"][0]["uuid"]
    portfolio = coin.client.get_portfolio_breakdown(portfolio_uuid)
    accounts = coin.client.get_accounts()
    for account in accounts["accounts"]:
        try:
            ticker = str(account.currency) + "-USD"
            amount = float(account.available_balance["value"])
            if amount > 0.01 and "USD" not in ticker.split("-")[0]:
                bid_ask = coin.client.get_best_bid_ask(ticker)["pricebooks"][0]
                bid = float(bid_ask["bids"][0]["price"])
                ask = float(bid_ask["asks"][0]["price"])    
                sell_order_id = Utils.generate_client_order_id()
                print(coin.client.limit_order_fok_sell(
                                        client_order_id=sell_order_id
                                        ,product_id=ticker
                                        ,limit_price=str(bid) 
                                        ,base_size=str(amount)))
        except Exception as e:
            print(str(e))
            continue