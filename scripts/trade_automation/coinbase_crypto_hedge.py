## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from common.database.adatabase import ADatabase
from common.extractor.coinbase_extractor import CoinbaseExtractor  
from common.extractor.alpaca_extractor import AlpacaExtractor
from financial_common.portfolio_management.portfolio import Portfolio
from common.processor.utils import Utils
import pandas as pd

ori = ADatabase("ori")
coin = CoinbaseExtractor()
alp = AlpacaExtractor(paper=False)
end = pd.to_datetime(alp.clock()["date"])

ori.cloud_connect()
top = ori.retrieve("crypto_results").to_dict("records")[0]
ori.disconnect()

pm = Portfolio.from_dict(top)

if end.hour == 15:
    portfolio_uuid = coin.client.get_portfolios("DEFAULT")["portfolios"][0]["uuid"]
    portfolios = [x.__dict__ for x in coin.client.get_portfolio_breakdown(portfolio_uuid)["breakdown"].__dict__["spot_positions"]]
    positions = pd.DataFrame(portfolios)
    accounts = coin.client.get_accounts()
    for account in accounts["accounts"]:
        try:
            ticker = str(account.currency) + "-USD"
            amount = float(account.available_balance["value"])
            if amount > 0.01 and "USD" not in ticker.split("-")[0]:
                position = positions[positions["asset"]==account.currency].iloc[0]
                adjclose = float(position["average_entry_price"]["value"])
                stop_price = round(adjclose * (1-pm.stoploss-0.01),3)
                limit_price = round(adjclose * (1-pm.stoploss),3) 
                sell_order_id = Utils.generate_client_order_id()
                print(coin.client.stop_limit_order_gtc_sell(
                                        client_order_id=sell_order_id,
                                        product_id=ticker
                                        ,stop_price=str(stop_price)
                                        ,stop_direction="STOP_DIRECTION_STOP_DOWN"
                                        ,limit_price=str(limit_price) 
                                        ,base_size=str(amount)))
        except Exception as e:
            print(str(e))
            continue