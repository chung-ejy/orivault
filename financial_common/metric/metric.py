from enum import Enum
import numpy as np

class Metric(Enum):
    AVERAGE_RETURN = ("average_return", lambda: AverageReturn())
    STANDARD_DEV = ("standard_dev", lambda: StandardDev())

    def __init__(self, label, calculation_method):
        self.label = label
        self.calculation_method = calculation_method

    def calculate(self, price, timeframe=100, live=False):
        """Calculate reference values, add computed indicator values to the dataframe, and return the updated dataframe."""
        cols = self.get_columns(live)
        if not live:
            price[cols["price"]] = price["adjclose"].shift(1)
            price[cols["volume"]] = price["adjvolume"].shift(1)
            price[cols["high"]] = price["adjhigh"].shift(1)
            price[cols["low"]] = price["adjlow"].shift(1)
        
        price[self.label] = self.calculation_method().calculate(price, timeframe, live)
        return price

    @classmethod
    def get_columns(cls, live):
        """Return column mappings based on live or non-live mode."""
        if live:
            return {
                "price": "adjclose",
                "high": "high",
                "low": "low",
                "volume": "volume"
            }
        else:
            return {
                "price": "reference_price",
                "high": "reference_high",
                "low": "reference_low",
                "volume": "reference_volume"
            }

    @classmethod
    def indicator_type_factory(cls, indicator_type):
        mapping = {member.label: member for member in cls}
        return mapping.get(indicator_type, None)

    def __str__(self):
        return self.label
    
class AverageReturn:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Metric.get_columns(live)
        return (price[cols["price"]]).pct_change(5).rolling(window=timeframe).mean()

class StandardDev:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Metric.get_columns(live)
        return price[cols["price"]].rolling(timeframe).std()