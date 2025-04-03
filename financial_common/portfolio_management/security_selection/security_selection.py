from financial_common.portfolio_management.security_selection.selection_type import SelectionType

class SecuritySelection(object):

    def __init__(self, strategy):
        self.strategy = SelectionType.selection_factory(strategy)

    def select(self, group, percentage,asset_type):
        return self.strategy.select(group, percentage, asset_type)