from flask import Flask, request, jsonify
## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from common.processor.utils import Utils
from common.extractor.alpaca_extractor import AlpacaExtractor  
from datetime import timedelta
from flask_cors import CORS  # Import Flask-CORS


alp = AlpacaExtractor(paper=False)
app = Flask(__name__)
CORS(app, origins=["http://localhost:5000","http://localhost:5173", "https://oritude.onrender.com"])

def base_response():
    return {"data":""}

@app.route('/api/tickers', methods=['GET'])
def tickers():
    response = base_response()
    index = alp.assets()
    response["data"] = list(index["ticker"].values)
    return jsonify(response)

@app.route('/api/quotes', methods=['POST'])
def quotes():
    data = request.json
    response = base_response()
    end = Utils.last_weekday(alp.clock())
    start = end - timedelta(days=2)
    quotes = alp.quotes(data["ticker"],start,end)
    response["data"] = quotes.drop("c",axis=1).to_dict("records")
    return jsonify(response)

@app.route('/api/trades', methods=['POST'])
def trades():
    data = request.json
    response = base_response()
    end = Utils.last_weekday(alp.clock())
    start = end - timedelta(days=2)
    trades = alp.trades(data["ticker"],start,end)
    response["data"] = trades.drop("c",axis=1).to_dict("records")
    return jsonify(response)

@app.route('/api/quote', methods=['POST'])
def quote():
    data = request.json
    response = base_response()
    quote = alp.latest_quote(data["ticker"])
    response["data"] = quote
    return jsonify(response)

@app.route('/api/trade', methods=['POST'])
def trade():
    data = request.json
    response = base_response()
    trade = alp.latest_trade(data["ticker"])
    response["data"] = trade
    return jsonify(response)

@app.route('/api/bar', methods=['POST'])
def bar():
    data = request.json
    response = base_response()
    bar = alp.latest_bar(data["ticker"])
    response["data"] = bar
    return jsonify(response)

@app.route('/api/bars', methods=['POST'])
def bars():
    data = request.json
    response = base_response()
    end = Utils.last_weekday(alp.clock())
    start = end - timedelta(days=2)
    bar = alp.prices_hour(data["ticker"],start,end)
    response["data"] = bar.to_dict("records")
    return jsonify(response)

@app.route('/api/options', methods=['POST'])
def options():
    data = request.json
    response = base_response()
    end = Utils.last_weekday(alp.clock())
    try:
        index = alp.call_options(data["ticker"],end)
        contracts = list(index)
        contracts.sort()
    except:
        contracts = []
    response["data"] = contracts
    return jsonify(response)

@app.route('/api/options/quote', methods=['POST'])
def option_quote():
    data = request.json
    response = base_response()
    quote = alp.latest_option_quote(data["ticker"])
    response["data"] = quote
    return jsonify(response)

@app.route('/api/options/trade', methods=['POST'])
def option_trade():
    data = request.json
    response = base_response()
    trade = alp.latest_option_trade(data["ticker"])
    response["data"] = trade
    return jsonify(response)

@app.route('/api/orders',methods=["GET"])
def orders():
    response = base_response()
    orders = alp.orders()
    print(orders.head())
    response["data"] = orders.fillna("").to_dict("records")
    return jsonify(response)

@app.route('/api/orders',methods=["DELETE"])
def cancel_order():
    data = request.json
    response = base_response()
    try:
        alp.cancel_order(data["order_id"])
        response["data"] = "Order cancelled successfully"
    except Exception as e:
        response["data"] = str(e)
    return jsonify(response)

@app.route('/api/positions',methods=["GET"])
def positions():
    response = base_response()
    positions = alp.positions()
    response["data"] = positions.fillna("").to_dict("records")
    return jsonify(response)

@app.route('/api/account',methods=["GET"])
def account():
    response = base_response()
    account = alp.account()
    response["data"] = account
    return jsonify(response)

@app.route('/api/buy', methods=['POST'])
def buy():
    data = request.json
    response = base_response()
    data["side"] = "buy"
    try:
        alp.buy(data["ticker"], float(data["adjclose"]), float(data["qty"]))
        response["data"] = "Buy order placed successfully"
    except Exception as e:
        response["data"] = str(e)
    return jsonify(response)

@app.route('/api/sell', methods=['POST'])
def sell():
    data = request.json
    data["side"] = "sell"
    response = base_response()
    print(data)
    # try:
    #     alp.sell(data["ticker"], float(data["adjclose"]), float(data["qty"]))
    #     response["data"] = "sell order placed successfully"
    # except Exception as e:
    #     response["data"] = str(e)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)