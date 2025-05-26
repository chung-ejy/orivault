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
    print(end)
    index = alp.call_options(data["ticker"],end)
    contracts = list(index)
    contracts.sort()
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

if __name__ == '__main__':
    app.run(debug=True)