from financial_common.portfolio_management.security_selection.selection_type import SelectionType
from financial_common.portfolio_management.portfolio import Portfolio
from financial_common.assets.timeframe import Timeframe
from financial_common.assets.position_type import PositionType
from itertools import product

class PortfolioSelection:
    
    @staticmethod
    def generate_possible_portfolios(group_percentages=[0.01], grouping_columns=["sic_description"], ranking_metrics=["factor"]):
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

        if not isinstance(grouping_columns, list) or not isinstance(ranking_metrics, list):
            raise ValueError("grouping_columns and ranking_metrics must be lists.")

        # Generate portfolios for all combinations of parameters
        portfolios = []
        for grouping_column, ranking_metric, timeframe, group_percentage, selection_type, position_type in product(
                grouping_columns, ranking_metrics, Timeframe, group_percentages, SelectionType, PositionType):
            
            portfolio = Portfolio(
                grouping_column=grouping_column,
                ranking_metric=ranking_metric,
                timeframe=timeframe.value,
                position_type=position_type.label,
                selection_type=selection_type.label,
                selection_percentage=group_percentage
            )
            portfolios.append(portfolio)
        
        return portfolios