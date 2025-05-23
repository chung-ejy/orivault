from flask import Flask, request, jsonify
## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from common.processor.processor import Processor as p
from common.extractor.alpaca_extractor import AlpacaExtractor  
from financial_common.portfolio_management.portfolio import Portfolio
from financial_common.risk.risk_type import RiskType
from financial_common.indicator.indicator import Indicator
from financial_common.metric.metric import Metric
from financial_common.portfolio_management.security_selection.grouping_type import GroupingType
from financial_common.assets.position_type import PositionType
from financial_common.assets.timeframe import Timeframe
from financial_common.portfolio_management.security_allocation.allocation_type import AllocationType
from financial_common.portfolio_management.security_selection.selection_type import SelectionType
from financial_common.risk.benchmark import Benchmark
from financial_common.portfolio_management.kpi import KPI
import pandas as pd
from datetime import timedelta
from flask_cors import CORS  # Import Flask-CORS


app = Flask(__name__)
CORS(app, origins=["http://localhost:5000","http://localhost:5173", "https://oritude.onrender.com"])
def base_response():
    return {"data":""}

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/api/position_type', methods=['GET'])
def position_type():
    response = base_response()
    response["data"] = [x.label for x in PositionType]
    return jsonify(response)

@app.route('/api/timeframe', methods=['GET'])
def timeframe():
    response = base_response()
    response["data"] = [x.value for x in Timeframe]
    return jsonify(response)

@app.route('/api/indicator', methods=['GET'])
def indicator():
    response = base_response()
    response["data"] = [x.label for x in Indicator]
    return jsonify(response)

@app.route('/api/grouping_type', methods=['GET'])
def grouping_type():
    response = base_response()
    response["data"] = [x.value for x in GroupingType]
    return jsonify(response)

@app.route('/api/risk_type', methods=['GET'])
def risk_type():
    response = base_response()
    response["data"] = [x.label for x in RiskType]
    return jsonify(response)

@app.route('/api/allocation_type', methods=['GET'])
def allocation_type():
    response = base_response()
    response["data"] = [x.label for x in AllocationType]
    return jsonify(response)

@app.route('/api/selection_type', methods=['GET'])
def selection_type():
    response = base_response()
    response["data"] = [x.label for x in SelectionType]
    return jsonify(response)

@app.route('/api/backtest', methods=['POST'])
def backtest():
    data = request.json  # Extract JSON data from the request body
    paper = False
    alp = AlpacaExtractor(paper=paper)
    end = pd.to_datetime(alp.clock()["date"])
    rolling_window = data["rolling_window"]
    delta_days = 365 + rolling_window
    index = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",attrs={"id":"constituents"})[0].rename(columns={"Symbol":"ticker"})
    tickers_per_batch = int(10000/delta_days/2)
    end = alp.clock()["date"] - timedelta(days=1)
    start = (end - timedelta(days=delta_days))
    prices = []
    tickers = list(index["ticker"].unique())
    batchs = [tickers[i:i + tickers_per_batch] for i in range(0, len(tickers), tickers_per_batch)]
    for batch in batchs:
        tickers_data = alp.prices_bulk(batch,start,end)
        dividends = alp.dividends(batch,start,end).rename(columns={"symbol":"ticker","record_date":"date"})[["date","rate","ticker"]]
        for ticker in batch:
            try:
                price = tickers_data[tickers_data["ticker"] == ticker].copy()
                dividends = dividends[dividends["ticker"]==ticker].copy()
                price = p.lower_column(price)
                price = p.utc_date(price)
                if dividends.index.size > 0:
                    dividends = p.utc_date(dividends)
                    price = price.merge(dividends,on=["date","ticker"])
                    price["dividend"] = price["rate"].ffill().fillna(0)
                else:
                    price["dividend"] = 0
                price.sort_values("date", inplace=True)
                price = p.additional_date_columns(price)
                price = Metric.NEXT_CLOSE.calculate(price,timeframe=rolling_window,live=False)
                price = Metric.indicator_type_factory(data["grouping_type"].lower()).calculate(price,timeframe=rolling_window,live=False)
                price = Indicator.indicator_type_factory(data["ranking_metric"].lower()).calculate(price,timeframe=rolling_window,live=False)
                price = RiskType.risk_type_factory(data["risk_type"].lower()).apply(price)
                prices.append(price)
            except Exception as e:
                print(str(e))

    simulation = pd.concat(prices)
    simulation.sort_values("date", inplace=True)
    pm = Portfolio.from_dict(data)
    benchmark = alp.prices("SPY",start,end)
    benchmark = Benchmark.convert_to_benchmark(benchmark,"adjclose")
    trades = pm.trades(simulation.copy()).sort_values("group_percentile", ascending=False)
    portfolio = pm.portfolio(trades,benchmark)
    portfolio["date"] = [x.strftime("%Y-%m-%d") for x in portfolio["date"]]
    trades["date"] = [x.strftime("%Y-%m-%d") for x in trades["date"]]
    performance = KPI.performance(trades,portfolio)
    response = base_response()
    backtest_data = {
        "trades":trades[["date","ticker","return","weight","adjclose","sell_price"]].dropna().round(4).to_dict("records"),
        "portfolio":portfolio[["date","pnl","benchmark_pnl"]].dropna().round(4).to_dict("records"),
        "metrics":pd.DataFrame([performance]).dropna().round(3).to_dict("records")[0]
    }
    response["data"] = backtest_data
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)