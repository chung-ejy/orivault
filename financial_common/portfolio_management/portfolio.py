from financial_common.trading.trades import Trades
from financial_common.portfolio_management.security_selection.selection_type import SelectionType
from financial_common.portfolio_management.security_allocation.allocation_type import AllocationType
from financial_common.risk.risk_type import RiskType
from financial_common.assets.position_type import PositionType
from scipy.stats.mstats import winsorize
from common.processor.processor import Processor as p
from enum import Enum
class Portfolio(object):

    def __init__(self, timeframe, ranking_type, position_type, selection_type, allocation_type, risk_type, selection_percentage, grouping_column):
        self.timeframe = timeframe  # Timeframe of the assets (e.g., week, month, quarter)
        self.ranking_type = ranking_type  # Metric used to rank the securities
        self.position_type = PositionType.get_position_type(position_type)
        self.selection_type = SelectionType.selection_type_factory(selection_type)
        self.allocation_type = AllocationType.allocation_type_factory(allocation_type)
        self.risk_type = RiskType.risk_type_factory(risk_type)
        self.selection_percentage = selection_percentage  # Percentage of securities to select from the ranked list
        self.grouping_column = grouping_column  # Column used to group the securities (e.g., sector, market cap)

    def trades(self, sim):
        trades = Trades.timeframe_trades(sim.copy(), factor=self.ranking_metric,timeframe=self.timeframe, group=self.grouping_column,risk=self.risk_type)
        trades = trades.sort_values(self.ranking_metric)
        trades["risk"] = trades[self.risk_type.label]
        trades = trades.groupby(["year", self.timeframe,self.grouping_column], group_keys=False).apply(
            lambda group: self.selection_type.select(group, self.selection_percentage,self.position_type),
            include_groups=False
        ).reset_index(drop=True)
        trades = trades.groupby(["date"],group_keys=False).apply(lambda group: self.allocation_type.allocate(group),include_groups=True).reset_index(drop=True)
        trades["unweighted_return"] = (trades["sell_price"] / trades["adjclose"] - 1) * trades["position_type"] + 1
        trades["winsorized_return"] = winsorize(trades["unweighted_return"], [0.05, 0.05])
        trades["return"] = (trades["winsorized_return"] - 1) * trades["weight"] + 1
        return trades
    
    def timeframe_trades(self,sim):
        sim["sell_price"] = sim["adjclose"]
        sim["sell_date"] = sim["date"]
        query = {"date":"last","adjclose":"first","sell_price":"last"}
        query[self.grouping_type.value] = "first"
        query[self.ranking_metric] = "first"
        query[self.risk_type.label] = "first"
        query[self.selection_type.label] = "first"
        timeframe_sim = sim.groupby(["year",self.timeframe,"ticker"]).agg(query).reset_index().sort_values("date")
        if self.timeframe=="week":
            timeframe_sim = timeframe_sim[(timeframe_sim[self.timeframe] != 1) & (timeframe_sim[self.timeframe] < 52)].sort_values("date")
        return timeframe_sim
    
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
