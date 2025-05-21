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
from financial_common.portfolio_management.portfolio import Portfolio
import pandas as pd

ori = ADatabase("ori")
coin = CoinbaseExtractor()
alp = AlpacaExtractor(paper=False)
end = pd.to_datetime(alp.clock()["date"])

ori.cloud_connect()
recs = ori.retrieve("crypto_recommendations").sort_values("group_percentile",ascending=False).head(10)
top = ori.retrieve("crypto_results").to_dict("records")[0]
ori.disconnect()
pm = Portfolio.from_dict(top)

if end.hour == 15:
    accounts = coin.client.get_accounts()
    cash = float([x.available_balance["value"] for x in accounts["accounts"] if x.currency == "USD"][0])
    for row in recs.iterrows():
        try:
            ticker = row[1]["ticker"]
            bid_ask = coin.client.get_best_bid_ask(ticker)["pricebooks"][0]
            bid = float(bid_ask["bids"][0]["price"])
            ask = float(bid_ask["asks"][0]["price"])  
            allocation = int(cash*row[1]["weight"]) if top["allocation_type"] != "equal" else int(cash/recs.index.size)
            buy_order_id = Utils.generate_client_order_id()
            qty = int(allocation / ask)
            print(coin.client.limit_order_fok_buy(
                                                client_order_id=Utils.generate_client_order_id(),
                                                product_id=str(ticker)
                                                ,base_size=str(qty)
                                                ,limit_price=str(ask)))
        except Exception as e:
            print(str(e))
            continue