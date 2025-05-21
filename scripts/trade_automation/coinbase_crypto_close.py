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

ori = ADatabase("ori")
coin = CoinbaseExtractor()
alp = AlpacaExtractor(paper=False)

ori.cloud_connect()
recs = ori.retrieve("crypto_recommendations").sort_values("group_percentile",ascending=False).head(10)
top = ori.retrieve("crypto_results").to_dict("records")[0]
ori.disconnect()

# # closing
portfolio_uuid = coin.client.get_portfolios("DEFAULT")["portfolios"][0]["uuid"]
portfolio = coin.client.get_portfolio_breakdown(portfolio_uuid)
accounts = coin.client.get_accounts()
orders = coin.client.list_orders(order_status="OPEN")["orders"]
for order in orders:
    coin.client.cancel_orders([order.order_id for order in orders])

sleep(5)
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