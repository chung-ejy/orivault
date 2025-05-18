from enum import Enum
import numpy as np

class RiskType(Enum):
    COEFFICIENT_OF_VARIATION = ("coefficient_of_variation", lambda: CoefficientOfVariation())

    def __init__(self, label, risk_method):
        self.label = label
        self.risk_method = risk_method

    def apply(self, df,timeframe=20):
        """Invoke the associated risk method."""
        return self.risk_method().apply(df,timeframe)
    
    @classmethod
    def risk_type_factory(cls, risk_type):
        mapping = {member.label: member for member in cls}
        return mapping.get(risk_type, None)
    
    def __str__(self):
        return self.label

class CoefficientOfVariation:
    @staticmethod
    def apply(df,timeframe=20):
        df.sort_values("date",inplace=True)
        df["coefficient_of_variation"] = df["adjclose"].rolling(timeframe).std() / df["adjclose"].rolling(timeframe).mean()
        return df