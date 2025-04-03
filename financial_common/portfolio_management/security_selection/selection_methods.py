import numpy as np

class MixedSelection:

    @staticmethod
    def select(group,percentage,asset_type):
        """
        Select a symmetric subset of rows from the group based on percentage.
        
        Parameters:
        - group (DataFrame): Grouped data (e.g., from df.groupby()).
        - percentage (float): Percentage of rows to select (0 < percentage <= 1).
                
        Returns:
        - DataFrame: Selected subset of rows.
        """
        def mixed_allocation_percentage(n, percentage):
            k = max(1, int(n * percentage))  # Total rows to select
            if k >= n:
                return np.arange(n)  # Take all if percentage >= 1
            
            mid = k // 2
            if k % 2 == 1:
                arr = np.arange(-mid, mid + 1)
            else:
                arr = np.arange(-mid, mid + 1)
                arr = np.delete(arr, mid)  # Remove 0 for symmetry
            return arr
        
        idx = mixed_allocation_percentage(len(group), percentage)
        selected_indices = group.index[idx % len(group)]  # Handle negative indexing safely
        group = group.loc[selected_indices].reset_index(drop=True)
        group["asset_type"] = group.index < int(group.index.size / 2)
        group["asset_type"] = group["asset_type"].map(lambda x: 1 if x else -1)
        return group 
    
class TopSelection:

    @staticmethod
    def select(group,percentage,asset_type):
        """
        Select the top subset of rows from the group based on percentage.
        
        Parameters:
        - group (DataFrame): Grouped data (e.g., from df.groupby()).
        - percentage (float): Percentage of rows to select (0 < percentage <= 1).
                
        Returns:
        - DataFrame: Selected subset of rows.
        """        
        n_rows = max(1, int(len(group) * percentage))
        trades = group.head(n_rows).reset_index(drop=True)
        trades["asset_type"] = asset_type.portfolio_effect
        return trades

class BottomSelection:
    @staticmethod
    def select(group, percentage,asset_type):
        """
        Select the bottom subset of rows from the group based on percentage.
        
        Parameters:
        - group (DataFrame): Grouped data (e.g., from df.groupby()).
        - percentage (float): Percentage of rows to select (0 < percentage <= 1).
                
        Returns:
        - DataFrame: Selected subset of rows.
        """        
        n_rows = max(1, int(len(group) * percentage))
        trades = group.tail(n_rows).reset_index(drop=True)
        trades["asset_type"] = asset_type.portfolio_effect
        return trades