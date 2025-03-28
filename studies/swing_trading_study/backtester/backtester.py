from diversifier.diversifier import Diversifier
from processor.processor import Processor as p
from scipy.stats.mstats import winsorize
import numpy as np
class Backtester(object):

    @classmethod
    def recommend(self,product,parameter):
        # Filter and sort data once
        market_cap_ceiling = parameter["market_cap_ceiling"]
        market_cap_floor = parameter["market_cap_floor"]
        direction = parameter["direction"]
        stocks = parameter["num_stocks"]
        signal = parameter["signal"]
        ascending = parameter["ascending"]
        percentage = float(stocks / 100)
        filtered = product[
            (product["market_cap_rank"] <= market_cap_ceiling) & 
            (product["market_cap_rank"] >= market_cap_floor)
        ]
        sorted_data = filtered.sort_values(signal, ascending=ascending)

        # Create a flag to check if direction is 0 or not
        is_direction_zero = direction == 0

        if is_direction_zero:
            trades = sorted_data.groupby(["year", "week"], group_keys=False).apply(
                lambda group: Diversifier.select_mixed_percentage(group, percentage), 
                include_groups=False
            ).reset_index(drop=True)

            trades["direction"] = trades.index < int(trades.index.size / 2)
            trades["direction"] = trades["direction"].map(lambda x: 1 if x else -1)
            trades["return"] = (trades["sell_price"] / trades["adjclose"] - 1) * trades["direction"] + 1
        else:
            trades = sorted_data.groupby(["year", "week"], group_keys=False).apply(
                lambda group: Diversifier.select_top_percentage(group, percentage), 
                include_groups=False
            ).reset_index(drop=True)
            trades["direction"] = direction
            trades["return"] = (trades["sell_price"] / trades["adjclose"] - 1) * trades["direction"] + 1
        return trades
    
    @classmethod
    def create_portfolio(self,trades,benchmark):
        # Portfolio calculations
        portfolio = trades.groupby("date", as_index=False).agg({"return": "mean"}).sort_values("date")
        portfolio = p.column_date_processing(portfolio)
        portfolio["pnl"] = portfolio["return"].cumprod()

        # Merge benchmark data once
        portfolio = portfolio.merge(benchmark[["date", "benchmark"]], on="date", how="left").dropna()
        portfolio["benchmark_pnl"] = portfolio["benchmark"] / portfolio["benchmark"].iloc[0]
        return portfolio

    @classmethod
    def run_strategy(self,product, parameter,benchmark):
        stoploss = parameter["stoploss"]
        filter_rate = parameter["filter_rate"]
        trades = self.recommend(product.copy(),parameter)
        if trades.index.size > 0:
            # Filter out extreme values early (for faster slicing)
            trades.sort_values("return",inplace=True)
            trades["return"] = winsorize(trades["return"], limits=[filter_rate, filter_rate])
            portfolio = self.create_portfolio(trades,benchmark)
            if portfolio.index.size > 0:
                metrics = self.performance(trades,portfolio)
                # Collect results and apply scoring
                results = {**parameter, **metrics}
            else:
                results = parameter.copy()
                results["pnl"] = -1
                results["outperformance_ratio"] = -np.inf
                trades = None
                portfolio = None
        else:
            results = parameter.copy()
            results["pnl"] = -1
            results["outperformance_ratio"] = -np.inf
            trades = None
            portfolio = None
        return results, trades, portfolio
