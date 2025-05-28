from flask import Flask, request, jsonify
## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from common.processor.utils import Utils
from common.extractor.alpaca_extractor import AlpacaExtractor  
from common.extractor.polygon_extractor import PolygonExtractor
from datetime import timedelta
from flask_cors import CORS  # Import Flask-CORS
import pandas as pd

alp = AlpacaExtractor(paper=False)
poly = PolygonExtractor()
app = Flask(__name__)
CORS(app, origins=["http://localhost:5000","http://localhost:5173", "https://oritude.onrender.com"])

def base_response():
    return {"data":""}

@app.route('/api/info', methods=['POST'])
def info():
    response = base_response()
    try:
        data = request.json
        quote = poly.ticker_overview(data["ticker"])
        response["data"] = quote["results"]
    except Exception as e:
        response["data"] = {}
    return jsonify(response)

@app.route('/api/tickers', methods=['GET'])
def tickers():
    response = base_response()
    try:
        index = alp.assets()
        response["data"] = list(index["ticker"].values)
    except Exception as e:
        response["data"] = []
    return jsonify(response)

@app.route('/api/quotes', methods=['POST'])
def quotes():
    response = base_response()
    try:
        data = request.json
        end = Utils.last_weekday(alp.clock())
        start = end - timedelta(days=5)
        quotes = alp.quotes(data["ticker"], start, end)
        response["data"] = quotes.drop("c", axis=1).to_dict("records")
    except Exception as e:
        response["data"] = []
    return jsonify(response)

@app.route('/api/trades', methods=['POST'])
def trades():
    response = base_response()
    try:
        data = request.json
        end = Utils.last_weekday(alp.clock())
        start = end - timedelta(days=5)
        trades = alp.trades(data["ticker"], start, end)
        response["data"] = trades.drop("c", axis=1).to_dict("records")
    except Exception as e:
        response["data"] = []
    return jsonify(response)

@app.route('/api/quote', methods=['POST'])
def quote():
    response = base_response()
    try:
        data = request.json
        quote = alp.latest_quote(data["ticker"])
        response["data"] = quote
    except Exception as e:
        response["data"] = {}
    return jsonify(response)

@app.route('/api/trade', methods=['POST'])
def trade():
    response = base_response()
    try:
        data = request.json
        trade = alp.latest_trade(data["ticker"])
        response["data"] = trade
    except Exception as e:
        response["data"] = {}
    return jsonify(response)

@app.route('/api/bar', methods=['POST'])
def bar():
    response = base_response()
    try:
        data = request.json
        bar = alp.latest_bar(data["ticker"])
        response["data"] = bar
    except Exception as e:
        response["data"] = {}
    return jsonify(response)

@app.route('/api/daily_bars', methods=['POST'])
def daily_bars():
    response = base_response()
    try:
        data = request.json
        end = Utils.last_weekday(alp.clock())
        start = end - timedelta(days=365)
        bar = alp.prices(data["ticker"], start, end)
        response["data"] = bar.to_dict("records")
    except Exception as e:
        response["data"] = []
    return jsonify(response)

@app.route('/api/bars', methods=['POST'])
def bars():
    response = base_response()
    try:
        data = request.json
        end = Utils.last_weekday(alp.clock())
        start = end - timedelta(days=2)
        bar = alp.prices_hour(data["ticker"], start, end)
        response["data"] = bar.to_dict("records")
    except Exception as e:
        response["data"] = []
    return jsonify(response)

@app.route('/api/options', methods=['POST'])
def options():
    response = base_response()
    try:
        data = request.json
        end = Utils.last_weekday(alp.clock())
        index = alp.call_options(data["ticker"], end)
        contracts = sorted(list(index))
        response["data"] = contracts
    except Exception as e:
        response["data"] = []
    return jsonify(response)

@app.route('/api/options/quote', methods=['POST'])
def option_quote():
    response = base_response()
    try:
        data = request.json
        quote = alp.latest_option_quote(data["ticker"])
        response["data"] = quote
    except Exception as e:
        response["data"] = {}
    return jsonify(response)

@app.route('/api/options/trade', methods=['POST'])
def option_trade():
    response = base_response()
    try:
        data = request.json
        trade = alp.latest_option_trade(data["ticker"])
        response["data"] = trade
    except Exception as e:
        response["data"] = {}
    return jsonify(response)

@app.route('/api/orders', methods=["GET"])
def orders():
    response = base_response()
    try:
        orders = alp.orders()
        response["data"] = orders.fillna("").to_dict("records")
    except Exception as e:
        response["data"] = []
    return jsonify(response)

@app.route('/api/orders', methods=["DELETE"])
def cancel_order():
    response = base_response()
    try:
        data = request.json
        alp.cancel_order(data["order_id"])
        response["data"] = "Order cancelled successfully"
    except Exception as e:
        response["data"] = str(e)
    return jsonify(response)

@app.route('/api/positions', methods=["GET"])
def positions():
    response = base_response()
    try:
        positions = alp.positions()
        response["data"] = positions.fillna("").to_dict("records")
    except Exception as e:
        response["data"] = []
    return jsonify(response)

@app.route('/api/account', methods=["GET"])
def account():
    response = base_response()
    try:
        account = alp.account()
        response["data"] = account
    except Exception as e:
        response["data"] = {}
    return jsonify(response)

@app.route('/api/buy', methods=['POST'])
def buy():
    response = base_response()
    try:
        data = request.json
        alp.buy(data["ticker"], float(data["adjclose"]), float(data["qty"]))
        response["data"] = "Buy order placed successfully"
    except Exception as e:
        response["data"] = str(e)
    return jsonify(response)

@app.route('/api/sell', methods=['POST'])
def sell():
    response = base_response()
    try:
        data = request.json
        alp.sell(data["ticker"], float(data["adjclose"]), float(data["qty"]))
        response["data"] = "Sell order placed successfully"
    except Exception as e:
        response["data"] = str(e)
    return jsonify(response)

@app.route('/api/analysis', methods=['POST'])
def analysis():
    response = base_response()
    try:
        data = request.json
        end = Utils.last_weekday(alp.clock())
        start = end - timedelta(days=5)
        quotes = alp.quotes(data["ticker"], start, end)
        trades = alp.trades(data["ticker"], start, end)
        
        analysis = quotes.merge(trades, on="t", how="outer", indicator=True).sort_values("t").ffill()[["t", "ap", "as", "bp", "bs", "p", "s"]].bfill().dropna()
        analysis["t"] = pd.to_datetime(analysis["t"])
        analysis["t"] = analysis["t"].dt.tz_convert("America/New_York")

        # Filter for market hours: 9:30 AM to 4:00 PM
        market_open = pd.to_datetime("09:30:00").time()
        market_close = pd.to_datetime("16:00:00").time()
        analysis = analysis[analysis["t"].dt.time.between(market_open, market_close)]
        response["data"] = analysis.to_dict("records")
    except Exception as e:
        response["data"] = []
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)