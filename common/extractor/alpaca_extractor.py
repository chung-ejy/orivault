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
        params = {
            "status":"active",
            "asset_class":"us_equity"
        }   
        requestBody = r.get(url,params=params,headers=self.headers)
        data = pd.DataFrame(requestBody.json()).rename(columns={"symbol":"ticker"})
        relevant_tickers = data[(data["marginable"]==True) & (data["tradable"]==True) & (data["fractionable"]==True) & (~data["exchange"].isin(["OTC","CRYPTO"]))].copy()[["ticker","marginable","exchange"]]
        return relevant_tickers
    
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
        return data["date"] 
    
    def latest_quote(self,ticker):
        params = {
            "feed":"delayed_sip"
        }
        url = f"https://data.alpaca.markets/v2/stocks/{ticker}/quotes/latest"
        requestBody = r.get(url,params=params,headers=self.headers)
        return requestBody.json()["quote"]
    
    def latest_trade(self,ticker):
        params = {
            "feed":"delayed_sip"
        }
        url = f"https://data.alpaca.markets/v2/stocks/{ticker}/trades/latest"
        requestBody = r.get(url,params=params,headers=self.headers)
        return requestBody.json()["trade"]
    
    def quotes(self,ticker,start,end):
        params = {
            "feed":"sip",
            "start":start.strftime("%Y-%m-%d"),
            "end":end.strftime("%Y-%m-%d"),
            "limit":3000,
            "sort":"desc"
        }
        url = f"https://data.alpaca.markets/v2/stocks/{ticker}/quotes"
        requestBody = r.get(url,params=params,headers=self.headers)
        return pd.DataFrame(requestBody.json()["quotes"])
    
    def trades(self,ticker,start,end):
        params = {
            "feed":"sip",
            "start":start.strftime("%Y-%m-%d"),
            "end":end.strftime("%Y-%m-%d"),
            "limit":3000,
            "sort":"desc"
        }
        url = f"https://data.alpaca.markets/v2/stocks/{ticker}/trades"
        requestBody = r.get(url,params=params,headers=self.headers)
        return pd.DataFrame(requestBody.json()["trades"])
    
    def latest_bar(self,ticker):
        params = {
            "feed":"delayed_sip"
        }
        url = f"https://data.alpaca.markets/v2/stocks/{ticker}/bars/latest"
        requestBody = r.get(url,params=params,headers=self.headers)
        return requestBody.json()["bar"]
    
    def latest_bars_bulk(self,tickers):
        tickers_string = ",".join(tickers)
        params = {
            "symbols":tickers_string,
            "feed":"delayed_sip"
        }
        url = "https://data.alpaca.markets/v2/stocks/bars/latest"
        requestBody = r.get(url,params=params,headers=self.headers)
        prices = []
        for ticker in tickers:
            try:
                data =  pd.DataFrame([requestBody.json()["bars"][ticker]]).rename(columns={"h":"high","l":"low","v":"volume","c":"adjclose","t":"date"})[["date","adjclose","high","low","volume"]]
                data["ticker"] = ticker
                prices.append(data)
            except Exception as e:
                print(str(e))
        return pd.concat(prices)
    
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
                data =  pd.DataFrame(requestBody.json()["bars"][ticker]).rename(columns={"h":"high","l":"low","v":"volume","o":"open","c":"adjclose","t":"date"})[["date","open","adjclose","high","low","volume"]]
                data["ticker"] = ticker
                prices.append(data)
            except Exception as e:
                print(str(e))
        return pd.concat(prices)
    
    def prices_minute(self,tickers,start,end):
        tickers_string = ",".join(tickers)
        params = {
            "symbols":tickers_string,
            "adjustment":"all",
            "timeframe":"10Min",
            "feed":"sip",
            "sort":"asc",
            "start":start.strftime("%Y-%m-%d"),
            "end":end.strftime("%Y-%m-%d")
        }
        url = "https://data.alpaca.markets/v2/stocks/bars"
        requestBody = r.get(url,params=params,headers=self.headers)
        print(requestBody.json())
        prices = []
        for ticker in tickers:
            data =  pd.DataFrame(requestBody.json()["bars"][ticker]).rename(columns={"h":"high","l":"low","v":"volume","o":"open","c":"close","t":"date"})[["date","close","open","high","low","volume"]]
            data["ticker"] = ticker
            prices.append(data)
        return pd.concat(prices)
    
    def prices_hour(self,ticker,start,end):
        params = {
            "symbols":ticker,
            "adjustment":"all",
            "timeframe":"1Hour",
            "feed":"sip",
            "sort":"asc",
            "start":start.strftime("%Y-%m-%d"),
            "end":end.strftime("%Y-%m-%d")
        }
        url = "https://data.alpaca.markets/v2/stocks/bars"
        requestBody = r.get(url,params=params,headers=self.headers)
        data =  pd.DataFrame(requestBody.json()["bars"][ticker]).rename(columns={"h":"high","l":"low","v":"volume","o":"open","c":"close","t":"date"})[["date","close","open","high","low","volume"]]
        data["ticker"] = ticker
        return data    
    
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
        data =  pd.DataFrame(requestBody.json()["bars"][ticker]).rename(columns={"h":"high","l":"low","v":"volume","o":"open","c":"adjclose","t":"date"})[["date","adjclose","open","high","low","volume"]]
        data["close"] = data["adjclose"]
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
    
    def buy_market(self,ticker,notional):
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
        
    def long_stop_loss(self,ticker,stop_price,quantity):
        data = {
            "side": "sell",
            "type": "stop_limit",
            "time_in_force": "day",
            "symbol": ticker,
            "limit_price": stop_price - 0.01,
            "stop_price": stop_price,
            "qty": quantity
            }
        url = f"{self.domain}/v2/orders"
        requestBody = r.post(url,json=data,headers=self.headers)
        return requestBody.json()
    
    def short_stop_loss(self,ticker,stop_price,quantity):
        data = {
            "side": "buy",
            "type": "stop_limit",
            "time_in_force": "day",
            "symbol": ticker,
            "limit_price": stop_price + 0.01,
            "stop_price": stop_price,
            "qty": quantity
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
    
    def orders(self):
        params = {
            "status":"open",
            "limit":100,
            # "after":(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            # "until":(self.clock()).strftime("%Y-%m-%d"),
            "direction":"desc",
            "nested":"false"
                  }
        url = f"{self.domain}/v2/orders"
        requestBody = r.get(url,params=params,headers=self.headers)
        return pd.DataFrame(requestBody.json())
    
    def cancel_orders(self):
        params = {}
        url = f"{self.domain}/v2/orders"
        requestBody = r.delete(url,params=params,headers=self.headers)
        return requestBody.json()
    
    def cancel_order(self,order_id):
        params = {}
        url = f"{self.domain}/v2/orders/{order_id}"
        requestBody = r.delete(url,params=params,headers=self.headers)
        return requestBody.json()
    
    def positions(self):
        params = {}
        url = f"{self.domain}/v2/positions"
        requestBody = r.get(url,params=params,headers=self.headers)
        return pd.DataFrame(requestBody.json())
    
    def close(self):
        params = {}
        url = f"{self.domain}/v2/positions?cancel_orders=true"
        requestBody = r.delete(url,params=params,headers=self.headers)
        return requestBody.json()
    
    def dividends(self,tickers,start,end):
        tickers_string = ",".join(tickers)
        params = {
            "symbols":tickers_string,
            "types":"cash_dividend",
            "start":start.strftime("%Y-%m-%d"),
            "end":end.strftime("%Y-%m-%d"),
            "limit":1000,

        }
        url = "https://data.alpaca.markets/v1/corporate-actions"
        requestBody = r.get(url,params=params,headers=self.headers)
        json_request = requestBody.json()["corporate_actions"]
        data =  pd.DataFrame(json_request["cash_dividends"])
        return data
    
    def call_options(self,ticker,asof_date):
        params = {
            "feed":"indicative",
            "limit":1000,
            "updated_since":asof_date.strftime("%Y-%m-%d"),
            "type":"call"
        }
        url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}"
        requestBody = r.get(url,params=params,headers=self.headers)
        json_request = requestBody.json()["snapshots"].keys()
        return json_request
    
    def put_options(self,ticker,asof_date):
        params = {
            "feed":"indicative",
            "limit":1000,
            "updated_since":asof_date.strftime("%Y-%m-%d"),
            "type":"put"
        }
        url = f"https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}"
        requestBody = r.get(url,params=params,headers=self.headers)
        json_request = requestBody.json()["snapshots"].keys()
        return json_request
    
    def latest_option_quote(self,ticker):
        params = {
            "symbols":ticker,
            "feed":"indicative"
        }
        url = f"https://data.alpaca.markets/v1beta1/options/quotes/latest"
        requestBody = r.get(url,params=params,headers=self.headers)
        print(requestBody.json())
        return requestBody.json()["quotes"][ticker]
    
    def latest_option_trade(self,ticker):
        params = {
            "symbols":ticker,
            "feed":"indicative"
        }
        url = f"https://data.alpaca.markets/v1beta1/options/trades/latest"
        requestBody = r.get(url,params=params,headers=self.headers)
        return requestBody.json()["trades"][ticker]