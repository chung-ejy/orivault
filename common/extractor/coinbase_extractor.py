from coinbase.rest import RESTClient

from dotenv import load_dotenv
load_dotenv()
import os
import pandas as pd

class CoinbaseExtractor(object):

    def __init__(self):
        self.client = RESTClient(os.getenv("COINBASEKEY"),os.getenv("COINBASESECRET"))
    
    def listed_crypto(self):
        data = pd.DataFrame([x.__dict__ for x in self.client.get_products(product_type="SPOT",get_tradability_status=True).__dict__["products"] \
                             if "-USD" == x["product_id"][-4:] and x["trading_disabled"] == False and x["status"] == "online" and x["quote_display_symbol"] == "USD"])
        return data[["product_id","status","trading_disabled"]].rename(columns={"product_id":"ticker","status":"status","trading_disabled":"trading_disabled"})
    
    def prices(self,ticker,start,end):
        price = self.client.get_candles(ticker,int(start.timestamp()),int(end.timestamp()),"ONE_DAY")
        candles = [x.__dict__ for x in price["candles"]]
        return pd.DataFrame(candles,columns=candles[0].keys())