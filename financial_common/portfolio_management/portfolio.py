from financial_common.portfolio_management.security_selection.selection_type import SelectionType
from financial_common.portfolio_management.security_allocation.allocation_type import AllocationType
from financial_common.portfolio_management.security_selection.optimization_selection_type import OptimizationSelectionType
from financial_common.portfolio_management.security_allocation.optimization_allocation_type import OptimizationAllocationType
from financial_common.portfolio_management.security_selection.grouping_type import GroupingType
from financial_common.assets.timeframe import Timeframe
from financial_common.risk.risk_type import RiskType
from financial_common.assets.position_type import PositionType
from scipy.stats.mstats import winsorize
from common.processor.processor import Processor as p
from enum import Enum
import warnings
warnings.simplefilter(action='ignore')

class Portfolio(object):

    def __init__(self, timeframe, ranking_metric, position_type, grouping_type, selection_type,  allocation_type, risk_type, selection_percentage):
        self.ranking_metric = ranking_metric  # Metric used to rank the securities
        self.timeframe = Timeframe.timeframe_factory(timeframe)  # Timeframe of the assets (e.g., week, month, quarter)
        self.position_type = PositionType.get_position_type(position_type)
        self.grouping_type = GroupingType.get_grouping_type(grouping_type)  # Type of grouping (e.g., sector, industry)
        self.selection_type = SelectionType.selection_type_factory(selection_type)
        self.allocation_type = AllocationType.allocation_type_factory(allocation_type)
        self.risk_type = RiskType.risk_type_factory(risk_type)
        self.selection_percentage = selection_percentage  # Percentage of securities to select

    def trades(self, sim):
        trades = self.timeframe_trades(sim.copy())
        trades = self.allocations(trades)
        trades["unweighted_return"] = (trades["sell_price"] / trades["adjclose"] - 1) * trades["position_type"] + 1
        trades["winsorized_return"] = winsorize(trades["unweighted_return"].copy(), [0.01, 0.01])
        trades["weighted_return"] = (trades["unweighted_return"]-1) * trades["weight"] + 1
        trades["return"] = (trades["winsorized_return"] - 1) * trades["weight"] + 1
        return trades
    
    def recs(self,sim):
        todays_sim = sim[sim["date"] == sim["date"].max()]
        trades = self.allocations(todays_sim)
        return trades

    def allocations(self,sim):
        trades = self.group_percentile_labeling(sim)
        trades = self.ranking_percentile_labeling(trades)
        trades = self.postprocessing(trades)
        trades = self.selection_type.select(trades, self.selection_percentage, self.position_type)
        trades = self.allocation_type.allocate(trades)    
        return trades
    
    def timeframe_trades(self,sim):
        sim["sell_price"] = sim["adjclose"]
        sim["sell_date"] = sim["date"]
        query = {"date":"last","adjclose":"first","sell_price":"last"}
        query[self.grouping_type.value] = "first"
        query[self.ranking_metric] = "first"
        query[self.risk_type.label] = "first"
        if self.allocation_type.label == "market_cap":
            query[self.allocation_type.label] = "first"
        timeframe_sim = sim.groupby(["year",self.timeframe.value,"ticker"]).agg(query).reset_index().sort_values("date")
        if self.timeframe.value=="week":
            timeframe_sim = timeframe_sim[(timeframe_sim[self.timeframe.value] != 1) & (timeframe_sim[self.timeframe.value] < 52)].sort_values("date")    
        return timeframe_sim
    
    def postprocessing(self,sim):
        sim.rename(columns={self.risk_type.label: "risk"}, inplace=True)
        sim["major_key"] = sim["year"].astype(str) + "_" + sim[self.timeframe.value].astype(str) + "_" + sim["group_percentile"].astype(str)
        return sim
    
    
    def group_percentile_labeling(self,sim):
        index = ["year", self.timeframe.value]
        sim = self.percentile_labeling(index, sim, self.grouping_type.value, "group", 1)
        return sim
    
    def ranking_percentile_labeling(self,sim): 
        index = ["year", self.timeframe.value,"group_percentile"]
        sim = self.percentile_labeling(index, sim, self.ranking_metric, "rank", 3)
        return sim
    
    def percentile_labeling(self,index,sim,column,name,decimals=3):
        """
        This function computes the percentile ranking of a given metric within a specified grouping.
        It returns the DataFrame with an additional column for the percentile rank.
        """
        sim.reset_index(drop=True, inplace=True)
        # Compute max index per group **without repeating groupby()**
        sim.sort_values(column, ascending=False, na_position="last",inplace=True)
        sim[f"{name}_idx"] = sim.groupby(index).cumcount() + 1
        group_max_idx = sim.groupby(index, as_index=False)[f"{name}_idx"].max().rename(columns={f"{name}_idx": f"{name}_idx_max"})
        sim = sim.merge(group_max_idx, on=index, how="left")
        # Ensure safe float division
        sim[f"{name}_idx_max"] = sim[f"{name}_idx_max"].astype(float)
        # Compute percentiles using safer rounding
        sim[f"{name}_percentile"] = round(sim[f"{name}_idx"] / sim[f"{name}_idx_max"] * 10 ** decimals) / 10 ** decimals
        sim.drop([f"{name}_idx", f"{name}_idx_max"], axis=1, inplace=True)
        return sim
    
    def portfolio(self, trades, benchmark):
        # Portfolio calculations
        portfolio = trades.groupby("date", as_index=False).agg({"weighted_return":"mean","return": "mean"}).sort_values("date")
        portfolio = p.lower_column(portfolio)
        portfolio = p.utc_date(portfolio).sort_values("date")
        portfolio["pnl"] = portfolio["return"].cumprod()
        portfolio["raw_pnl"] = portfolio["weighted_return"].cumprod()
        # Merge benchmark data once
        portfolio = portfolio.merge(benchmark[["date", "benchmark"]], on="date", how="left").dropna()
        portfolio["benchmark_pnl"] = portfolio["benchmark"] / portfolio["benchmark"].iloc[0]
        return portfolio.sort_values("date")
    
    
    def to_dict(self):
        """
        Custom method to serialize the object as a dictionary, replacing
        class strings with enum labels or names/values when labels are unavailable.
        """
        return {
            key: (
                getattr(value, "label", None) or getattr(value, "name", None) or value.value
                if isinstance(value, Enum) else value
            )
            for key, value in self.__dict__.items()
        }
    @staticmethod
    def from_dict(data):
        return Portfolio(timeframe=data["timeframe"].lower(), ranking_metric=data["ranking_metric"], position_type=data["position_type"], grouping_type=data["grouping_type"].lower(), selection_type=data["selection_type"], allocation_type=data["allocation_type"], risk_type=data["risk_type"], selection_percentage=data["selection_percentage"])

class OptimizedPortfolio(Portfolio):
    """
    Optimized Portfolio class that inherits from Portfolio.
    This class is used for creating optimized portfolios based on the given parameters.
    """
    def __init__(self, timeframe, ranking_metric, position_type, grouping_type, selection_type, allocation_type, risk_type, selection_percentage):
        super().__init__(timeframe, ranking_metric, position_type, grouping_type, selection_type, allocation_type, risk_type, selection_percentage)
        self.selection_type = OptimizationSelectionType.selection_type_factory(selection_type)
        self.allocation_type = OptimizationAllocationType.allocation_type_factory(allocation_type)
    
    @staticmethod
    def from_dict(data):
        return OptimizedPortfolio(timeframe=data["timeframe"].lower(), ranking_metric=data["ranking_metric"], position_type=data["position_type"], grouping_type=data["grouping_type"].lower(), selection_type=data["selection_type"], allocation_type=data["allocation_type"], risk_type=data["risk_type"], selection_percentage=data["selection_percentage"])