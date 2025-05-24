from enum import Enum
import numpy as np
import pandas as pd
from copy import deepcopy

class SelectionType(Enum):
    MIXED = ("mixed", lambda: MixedSelection())
    TOP = ("top", lambda: TopSelection())
    BOTTOM = ("bottom", lambda: BottomSelection())
    LONGSHORT = ("long_short", lambda: LongShortSelection())  # Placeholder for long/short selection
    TOP_BLACKLIST = ("top_blacklist",lambda: TopBlackListSelection())
    BOTTOM_BLACKLIST = ("bottom_blacklist",lambda: BottomBlackListSelection())

    def __init__(self, label, selection_method):
        self.label = label
        self.selection_method = selection_method

    def select(self, trades, percentage, position_type):
        """Invoke the associated selection method."""
        # Get max index within each group and broadcast it for each row
        return self.selection_method().select(trades, percentage, position_type)
    
    @classmethod
    def selection_type_factory(cls, selection_type):
        mapping = {member.label: member for member in cls}
        return mapping.get(selection_type, None)
    
    def __str__(self):
        return self.label

class MixedSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        # Compute indices within each group
        filtered = pd.concat([trades.groupby("major_key").first().reset_index(),trades.groupby("major_key").last().reset_index()])
        # Assign position type within grouping phase, avoiding post-processing
        filtered["position_type"] = position_type.portfolio_effect
        return filtered
    
class LongShortSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        # Compute indices within each group
        top = trades.groupby("major_key").first().reset_index()
        top["position_type"] = position_type.portfolio_effect
        bottom = trades.groupby("major_key").last().reset_index()
        bottom["position_type"] = -position_type.portfolio_effect
        filtered = pd.concat([top,bottom])
        return filtered

class TopSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        top = trades.groupby("major_key").first().reset_index()
        top["position_type"] = position_type.portfolio_effect
        return top

class TopBlackListSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        trades = trades.sort_values(["date", "rank_percentile"])  # Sort once for efficiency

        filtered_trades = []
        previous_blacklist, current_blacklist = set(), set()

        for major_key, date_trades in trades.groupby("major_key"):  
            daily_trade = date_trades.loc[~date_trades["ticker"].isin(previous_blacklist)].head(1)
            filtered_trades.append(daily_trade)

            current_blacklist.update(daily_trade["ticker"])  

            if len(current_blacklist) >= 3:  # More robust check
                previous_blacklist, current_blacklist = current_blacklist.copy(), set()  

        top = pd.concat(filtered_trades, ignore_index=True)  # `ignore_index=True` for efficiency
        top["position_type"] = position_type.portfolio_effect
        
        return top

class BottomBlackListSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        trades = trades.sort_values(["date", "rank_percentile"])  # Sort once for efficiency

        filtered_trades = []
        previous_blacklist, current_blacklist = set(), set()

        for major_key, date_trades in trades.groupby("major_key"):  
            daily_trade = date_trades.loc[~date_trades["ticker"].isin(previous_blacklist)].tail(1)
            filtered_trades.append(daily_trade)

            current_blacklist.update(daily_trade["ticker"])  

            if len(current_blacklist) >= daily_trade["group_percentile"].astype(int).max():  # More robust check
                previous_blacklist, current_blacklist = current_blacklist.copy(), set()  

        top = pd.concat(filtered_trades, ignore_index=True)  # `ignore_index=True` for efficiency
        top["position_type"] = position_type.portfolio_effect
        
        return top


class BottomSelection:
    @staticmethod
    def select(trades, percentage, position_type):
        bottom = trades.groupby("major_key").last().reset_index()
        bottom["position_type"] = position_type.portfolio_effect
        return bottom