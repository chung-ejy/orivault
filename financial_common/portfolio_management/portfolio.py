from financial_common.trading.trades import Trades
from financial_common.portfolio_management.security_selection.selection_type import SelectionType
from financial_common.assets.position_type import PositionType
from scipy.stats.mstats import winsorize
from common.processor.processor import Processor as p
from enum import Enum
class Portfolio(object):

    def __init__(self, timeframe, ranking_metric, position_type, selection_type, selection_percentage, grouping_column):
        self.timeframe = timeframe  # Timeframe of the assets (e.g., week, month, quarter)
        self.ranking_metric = ranking_metric  # Metric used to rank the securities
        self.position_type = PositionType.get_position_type(position_type)
        self.selection_type = SelectionType.selection_type_factory(selection_type)  # 1 for top percentage, 0 for mixed percentage, -1 for bottom percentage
        self.selection_percentage = selection_percentage  # Percentage of securities to select from the ranked list
        self.grouping_column = grouping_column  # Column used to group the securities (e.g., sector, market cap)

    def trades(self, sim):
        trades = Trades.timeframe_trades(sim.copy(), factor=self.ranking_metric,timeframe=self.timeframe, group=self.grouping_column)
        trades = trades.sort_values(self.ranking_metric)
        trades = trades.groupby(["year", self.timeframe,self.grouping_column], group_keys=False).apply(
            lambda group: self.selection_type.select(group, self.selection_percentage,self.position_type),
            include_groups=False
        ).reset_index(drop=True)
        trades["return"] = (trades["sell_price"] / trades["adjclose"] - 1) * trades["position_type"] + 1
        trades["return"] = winsorize(trades["return"], [0.05, 0.05])
        return trades

    def portfolio(self, trades, benchmark):
        # Portfolio calculations
        portfolio = trades.groupby("date", as_index=False).agg({"return": "mean"}).sort_values("date")
        portfolio = p.lower_column(portfolio)
        portfolio = p.utc_date(portfolio).sort_values("date")
        portfolio["pnl"] = portfolio["return"].cumprod()

        # Merge benchmark data once
        portfolio = portfolio.merge(benchmark[["date", "benchmark"]], on="date", how="left").dropna()
        portfolio["benchmark_pnl"] = portfolio["benchmark"] / portfolio["benchmark"].iloc[0]
        return portfolio.sort_values("date")
    
    
    def to_dict(self):
        """
        Custom method to serialize the object as a dictionary, replacing
        class strings with enum labels for specific attributes.
        """
        return {
            key: (value.label if isinstance(value, Enum) else value)
            for key, value in self.__dict__.items()
        }
