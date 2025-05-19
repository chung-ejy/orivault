import requests as r
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
import os

class AlpacaExtractor(object):
    
    def __init__(self,paper=False):
        self.key = os.getenv("APCAKEY")
        self.secret = os.getenv("APCASECRET")
        self.headers = {
                        'APCA-API-KEY-ID': self.key,
                        'APCA-API-SECRET-KEY': self.secret,
                        'accept': 'application/json'
                        }
        self.domain = "https://paper-api.alpaca.markets" if paper == True else "https://api.alpaca.markets"
    
    def assets(self):
        url = "https://api.alpaca.markets/v2/assets"
        requestBody = r.get(url,headers=self.headers)
        return requestBody.json()
    
    def clock(self):
        url = self.domain + "/v2/clock"
        requestBody = r.get(url,headers=self.headers)
        data = requestBody.json()
        iso_str = data["timestamp"]

        # Truncate fractional seconds to 6 digits
        date_part, tz_part = iso_str.split('-04:00')
        seconds, fraction = date_part.split('.')  # Split at decimal point
        fraction_truncated = fraction[:6]
        iso_fixed = f"{seconds}.{fraction_truncated}-04:00"

        # Convert to datetime
        data["date"] = datetime.fromisoformat(iso_fixed)
        return data
    
    def latest_bar(self,ticker):
        params = {
            "feed":"delayed_sip"
        }
        url = f"https://data.alpaca.markets/v2/stocks/{ticker}/bars/latest"
        requestBody = r.get(url,params=params,headers=self.headers)
        return requestBody.json()["bar"]
    
    def prices_bulk(self,tickers,start,end):
        tickers_string = ",".join(tickers)
        params = {
            "symbols":tickers_string,
            "adjustment":"all",
            "timeframe":"1Day",
            "feed":"sip",
            "sort":"asc",
            "start":start.strftime("%Y-%m-%d"),
            "end":end.strftime("%Y-%m-%d"),
            "limit":10000
        }
        url = "https://data.alpaca.markets/v2/stocks/bars"
        requestBody = r.get(url,params=params,headers=self.headers)
        prices = []
        for ticker in tickers:
            try:
                data =  pd.DataFrame(requestBody.json()["bars"][ticker]).rename(columns={"h":"high","l":"low","v":"volume","c":"adjclose","t":"date"})[["date","adjclose","high","low","volume"]]
                data["ticker"] = ticker
                prices.append(data)
            except Exception as e:
                print(str(e))
        return pd.concat(prices)
    
    def prices(self,ticker,start,end):
        params = {
            "symbols":ticker,
            "adjustment":"all",
            "timeframe":"1Day",
            "feed":"sip",
            "sort":"asc",
            "start":start.strftime("%Y-%m-%d"),
            "end":end.strftime("%Y-%m-%d")
        }
        url = "https://data.alpaca.markets/v2/stocks/bars"
        requestBody = r.get(url,params=params,headers=self.headers)
        data =  pd.DataFrame(requestBody.json()["bars"][ticker]).rename(columns={"h":"high","l":"low","v":"volume","c":"adjclose","t":"date"})[["date","adjclose","high","low","volume"]]
        data["ticker"] = ticker
        return data
    
    def asset_info(self,ticker):
        url = f"{self.domain}/v2/assets/{ticker}"
        requestBody = r.get(url,headers=self.headers)
        return requestBody.json()
    
    def account(self):
        params = {}
        url = f"{self.domain}/v2/account"
        requestBody = r.get(url,params=params,headers=self.headers)
        return requestBody.json()
    
    def buy(self,ticker,adjclose,quantity):
        data = {
            "side": "buy",
            "type": "limit",
            "time_in_force": "day",
            "symbol": ticker,
            "limit_price": adjclose,
            "qty": quantity
            }
        url = f"{self.domain}/v2/orders"
        requestBody = r.post(url,json=data,headers=self.headers)
        return requestBody.json()
    
    def buy_fraction(self,ticker,notional):
        data = {
            "side": "buy",
            "type": "market",
            "time_in_force": "day",
            "symbol": ticker,
            "notional": notional
            }
        url = f"{self.domain}/v2/orders"
        requestBody = r.post(url,json=data,headers=self.headers)
        return requestBody.json()
   
    def sell(self,ticker,adjclose,quantity):
        data = {
            "side": "sell",
            "type": "limit",
            "time_in_force": "day",
            "symbol": ticker,
            "limit_price": adjclose,
            "qty": quantity
            }
        url = f"{self.domain}/v2/orders"
        requestBody = r.post(url,json=data,headers=self.headers)
        return requestBody.json()
    
    def buy_stop_loss(self,ticker,adjclose,quantity,hedge_percentage):
        data = {
            "side": "buy",
            "symbol": ticker,
            "type": "limit",
            "limit_price":adjclose,
            "qty": quantity,
            "time_in_force": "day",
            "order_class": "oto",
            "stop_loss": {
                "stop_price": round(adjclose * float(1-hedge_percentage),4),
                "limit_price": round(adjclose * float(1-hedge_percentage-0.01),4)
            }
        }
        url = f"{self.domain}/v2/orders"
        requestBody = r.post(url,json=data,headers=self.headers)
        return requestBody.json()
    
    def sell_stop_loss(self, ticker, adjclose, quantity,hedge_percentage):
        data = {
            "side": "sell",  # Sell order for a short position
            "symbol": ticker,
            "type": "limit",
            "limit_price":adjclose,
            "qty": quantity,
            "time_in_force": "day",
            "order_class": "oto",  # One-Triggers-Other (OTO) order
            "stop_loss": {
                "stop_price": round(adjclose * float(1+hedge_percentage), 4),  # Stop loss triggered if price rises 5% above adjusted close
                "limit_price": round(adjclose * float(1+hedge_percentage+0.01), 4)  # The stop loss limit, slightly above the stop price
            }
        }
        url = f"{self.domain}/v2/orders"
        requestBody = r.post(url, json=data, headers=self.headers)
        return requestBody.json()
    
    def orders(self):
        params = {
            "status":"closed",
            "limit":500,
            "after":(datetime.now() - timedelta(days=365*1.5)).strftime("%Y-%m-%d"),
            "until":(datetime.now()).strftime("%Y-%m-%d"),
            "direction":"asc",
            "nested":"false"
                  }
        url = f"{self.domain}/v2/orders"
        requestBody = r.get(url,params=params,headers=self.headers)
        return requestBody.json()
    
    def close(self):
        params = {}
        url = f"{self.domain}/v2/positions?cancel_orders=true"
        requestBody = r.delete(url,params=params,headers=self.headers)
        return requestBody.json()
    