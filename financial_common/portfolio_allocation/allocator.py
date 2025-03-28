import numpy as np

class Allocator(object):

    @staticmethod    
    def select_mixed_percentage(group, percentage):
        def mixed_allocation_percentage(n, percentage):
            k = max(1, int(n * percentage))  # total rows to select
            if k >= n:
                return np.arange(n)  # take all if percentage >= 1

            mid = k // 2
            if k % 2 == 1:
                arr = np.arange(-mid, mid + 1)
            else:
                arr = np.arange(-mid, mid + 1)
                arr = np.delete(arr, mid)  # remove 0 for symmetry
            return arr
        idx = mixed_allocation_percentage(len(group), percentage)
        selected_indices = group.index[idx % len(group)]  # handle negative indexing safely
        return group.loc[selected_indices]
    
    @staticmethod    
    def select_top_percentage(group,percentage):
        n_rows = int(len(group) * percentage)
        return group.head(n_rows)