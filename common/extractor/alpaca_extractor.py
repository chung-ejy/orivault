import requests as r
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
import os

class AlpacaExtractor(object):
    
    def __init__(self):
        self.key = os.getenv("APCAKEY")
        self.secret = os.getenv("APCASECRET")
        self.headers = {
                        'APCA-API-KEY-ID': self.key,
                        'APCA-API-SECRET-KEY': self.secret,
                        'accept': 'application/json'
                        }
        
    def clock(self):
        url = "https://api.alpaca.markets/v2/clock"
        requestBody = r.get(url,headers=self.headers)
        return requestBody.json()
    
    def assets(self):
        url = "https://api.alpaca.markets/v2/assets"
        requestBody = r.get(url,headers=self.headers)
        return requestBody.json()
    
    def prices(self,ticker,start,end):
        params = {
            "symbols":ticker,
            "adjustment":"all",
            "timeframe":"1Day",
            "feed":"sip",
            "sort":"asc",
            "start":start.strftime("%Y-%m-%d"),
        }
        url = "https://data.alpaca.markets/v2/stocks/bars"
        requestBody = r.get(url,params=params,headers=self.headers)
        data =  pd.DataFrame(requestBody.json()["bars"][ticker]).rename(columns={"h":"high","l":"low","v":"volume","c":"adjclose","t":"date"})[["date","adjclose","high","low","volume"]]
        data["ticker"] = ticker
        return data
    
    def account(self):
        params = {}
        url = "https://api.alpaca.markets/v2/account"
        requestBody = r.get(url,params=params,headers=self.headers)
        return requestBody.json()

    def buy(self,ticker,notional):
        data = {
            "side": "buy",
            "type": "market",
            "time_in_force": "day",
            "symbol": ticker,
            "notional": notional
            }
        url = "https://api.alpaca.markets/v2/orders"
        requestBody = r.post(url,json=data,headers=self.headers)
        return requestBody.json()
    
    def sell(self,ticker,notional):
        data = {
            "side": "sell",
            "type": "market",
            "time_in_force": "day",
            "symbol": ticker,
            "notional": notional
            }
        url = "https://api.alpaca.markets/v2/orders"
        requestBody = r.post(url,json=data,headers=self.headers)
        return requestBody.json()
    
    def buy_stop_loss(self,ticker,adjclose,notional):
        data = {
            "side": "buy",
            "symbol": ticker,
            "type": "market",
            "notional": notional,
            "time_in_force": "day",
            "order_class": "oto",
            "stop_loss": {
                "stop_price": round(adjclose * 0.95,2),
                "limit_price": round(adjclose * 0.94,2)
            }
        }
        url = "https://api.alpaca.markets/v2/orders"
        requestBody = r.post(url,json=data,headers=self.headers)
        return requestBody
    
    def sell_stop_loss(self, ticker, adjclose, notional):
        data = {
            "side": "sell",  # Sell order for a short position
            "symbol": ticker,
            "type": "limit",  # Limit order for the sell
            "limit_price": round(adjclose * 0.95, 2),  # Sell at 5% below the adjusted close
            "notional": notional,
            "time_in_force": "day",
            "order_class": "oto",  # One-Triggers-Other (OTO) order
            "stop_loss": {
                "stop_price": round(adjclose * 1.05, 2),  # Stop loss triggered if price rises 5% above adjusted close
                "limit_price": round(adjclose * 1.06, 2)  # The stop loss limit, slightly above the stop price
            }
        }
        url = "https://api.alpaca.markets/v2/orders"
        requestBody = r.post(url, json=data, headers=self.headers)
        return requestBody
    
    def close(self):
        params = {}
        url = "https://api.alpaca.markets/v2/positions?cancel_orders=true"
        requestBody = r.delete(url,params=params,headers=self.headers)