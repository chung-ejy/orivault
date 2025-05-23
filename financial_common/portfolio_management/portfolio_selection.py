from financial_common.portfolio_management.security_selection.selection_type import SelectionType
from financial_common.portfolio_management.security_selection.optimization_selection_type import OptimizationSelectionType
from financial_common.portfolio_management.security_allocation.optimization_allocation_type import OptimizationAllocationType
from financial_common.portfolio_management.security_selection.grouping_type import GroupingType
from financial_common.portfolio_management.security_allocation.allocation_type import AllocationType
from financial_common.portfolio_management.portfolio import Portfolio
from financial_common.portfolio_management.portfolio import OptimizedPortfolio
from financial_common.risk.risk_type import RiskType
from financial_common.assets.timeframe import Timeframe
from financial_common.assets.position_type import PositionType
from itertools import product

class PortfolioSelection:
    
    @staticmethod
    def generate_possible_portfolios(ranking_metrics,group_percentages,num_of_groups,max_prices,min_prices,stoplosses,rolling_windows,leverages):
        """
        Generate all possible portfolios based on the given parameters.

        Args:
            group_percentage_minimum (float): Minimum percentage for the group (0 < percentage <= 1).
            group_percentage_maximum (float): Maximum percentage for the group (0 < percentage <= 1).
            grouping_columns (list): List of columns used for grouping.
            ranking_metrics (list): List of metrics used for ranking.

        Returns:
            list: List of possible portfolios.
        """
        # Generate portfolios for all combinations of parameters
        portfolios = []
        for ranking_metric, timeframe, group_percentage, grouping_type, selection_type, allocation_type, risk_type, position_type, num_of_group, max_price, min_price, stoploss, rolling_window, leverage in product(
            ranking_metrics, Timeframe, group_percentages, GroupingType, SelectionType, AllocationType, RiskType, PositionType, num_of_groups, max_prices, min_prices, stoplosses, rolling_windows, leverages):
            
            portfolio = Portfolio(
                ranking_metric=ranking_metric,
                timeframe=timeframe.value,
                position_type=position_type.label,
                grouping_type=grouping_type.value,
                selection_type=selection_type.label,
                allocation_type=allocation_type.label,
                risk_type=risk_type.label,
                selection_percentage=group_percentage,
                num_of_groups=num_of_group,
                stoploss=stoploss,
                max_price=max_price,
                min_price=min_price,
                rolling_window=rolling_window,
                leverage=leverage
            )
            portfolios.append(portfolio)
        
        return portfolios
    
    @staticmethod
    def optimize_portfolio(basic_portfolio,group_percentages=[0.01], ranking_metrics=["factor"]):
        """
        Generate all possible portfolios based on the given parameters.

        Args:
            group_percentage_minimum (float): Minimum percentage for the group (0 < percentage <= 1).
            group_percentage_maximum (float): Maximum percentage for the group (0 < percentage <= 1).
            grouping_columns (list): List of columns used for grouping.
            ranking_metrics (list): List of metrics used for ranking.

        Returns:
            list: List of possible portfolios.
        """
        # Validate inputs
        if not (0 <= min(group_percentages) <= 1 and 0 <= max(group_percentages) <= 1):
            raise ValueError("Group percentages must be between 0 and 1.")

        if not isinstance(ranking_metrics, list):
            raise ValueError("grouping_columns and ranking_metrics must be lists.")

        # Generate portfolios for all combinations of parameters
        portfolios = []
        for group_percentage , allocation_type in product(group_percentages, OptimizationAllocationType):
            portfolio = OptimizedPortfolio(
                ranking_metric=basic_portfolio.ranking_metric,
                timeframe=basic_portfolio.timeframe.value,
                position_type=basic_portfolio.position_type.label,
                grouping_type=basic_portfolio.grouping_type.value,
                selection_type=basic_portfolio.selection_type.label,
                allocation_type=allocation_type.label,
                risk_type=basic_portfolio.risk_type.label,
                selection_percentage=group_percentage
            )
            portfolios.append(portfolio)
        
        return portfolios