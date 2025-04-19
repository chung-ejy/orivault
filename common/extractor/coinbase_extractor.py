from coinbase.rest import RESTClient
from dotenv import load_dotenv
load_dotenv()
import os
import pandas as pd

class CoinbaseExtractor(object):

    def __init__(self):
        self.client = RESTClient(os.getenv("COINBASEKEY"),os.getenv("COINBASESECRET"))
    
    def listed_crypto(self):
        return [x["product_id"] for x in self.client.get_products(product_type="SPOT",get_tradability_status=True).__dict__["products"] if "-USD" in x["product_id"]]
    
    def prices(self,ticker,start,end):
        price = self.client.get_candles(ticker,int(start.timestamp()),int(end.timestamp()),"ONE_DAY")
        candles = [x.__dict__ for x in price["candles"]]
        return pd.DataFrame(candles,columns=candles[0].keys())