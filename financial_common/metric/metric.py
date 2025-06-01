from enum import Enum
from scipy.stats.mstats import winsorize
import numpy as np

class Metric(Enum):
    AVERAGE_RETURN = ("average_return", lambda: AverageReturn())
    STANDARD_DEV = ("standard_dev", lambda: StandardDev())
    MARKETCAP = ("market_cap", lambda: MarketCap())
    SIMPLE_MOVING_AVERAGE = ("simple_moving_average", lambda: SimpleMovingAverage())
    DRAWDOWN = ("drawdown", lambda: Drawdown())
    DISTANCE = ("distance", lambda: Distance())
    COOKED_RETURN = ("cooked_return", lambda: CookedReturn())
    NEXT_CLOSE = ("next_close", lambda: NextClose())
    NEXT_OPEN = ("next_open", lambda: NextOpen())
    DIVIDEND = ("dividend", lambda: Dividend())
    PriceToReturn = ("price_to_return", lambda: PriceToReturn())

    def __init__(self, label, calculation_method):
        self.label = label
        self.calculation_method = calculation_method

    def calculate(self, price, timeframe=100, live=False):
        """Calculate reference values, add computed indicator values to the dataframe, and return the updated dataframe."""
        cols = self.get_columns(live)        
        for col in ["adjclose", "high", "low", "volume"]:
            price[f"{col}_test"] = price[col].shift(1)
        
        price[self.label] = self.calculation_method().calculate(price, timeframe, live)
        return price

    @classmethod
    def get_columns(cls, live):
        """Return column mappings based on live or test mode."""
        return {
            "price": "adjclose" if live else "adjclose_test",
            "high": "high" if live else "high_test",
            "low": "low" if live else "low_test",
            "volume": "volume" if live else "volume_test"
        }

    @classmethod
    def indicator_type_factory(cls, indicator_type):
        mapping = {member.label: member for member in cls}
        return mapping.get(indicator_type, None)

    def __str__(self):
        return self.label

# ---- Updated Indicators ---- #
class SimpleMovingAverage:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Metric.get_columns(live)
        return price[cols["price"]].rolling(window=timeframe).mean()

class NextClose:
    @staticmethod
    def calculate(price, timeframe, live):
        return price["adjclose"].shift(-1)

class NextOpen:
    @staticmethod
    def calculate(price, timeframe, live):
        return price["open"].shift(-1)

class Drawdown:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Metric.get_columns(live)
        return (price[cols["price"]].rolling(window=timeframe).max() - price[cols["price"]]) / price[cols["price"]]

class AverageReturn:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Metric.get_columns(live)
        return price[cols["price"]].pct_change(5).rolling(window=timeframe).mean()

class StandardDev:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Metric.get_columns(live)
        return price[cols["price"]].rolling(timeframe).std()

class Distance:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Metric.get_columns(live)

        w = winsorize(price["dividend"].rolling(window=timeframe).mean().bfill().values, [0.01, 0.01])
        x = winsorize(price[cols["price"]].rolling(window=timeframe).mean().bfill().values, [0.01, 0.01])
        y = winsorize(price[cols["price"]].pct_change(5).rolling(window=timeframe).std().bfill(), [0.01, 0.01])
        z = winsorize(price[cols["price"]].pct_change(5).rolling(window=timeframe).mean().bfill(), [0.01, 0.01])

        def scale_to_range(arr):
            return 2 * (arr - np.nanmin(arr)) / (np.nanmax(arr) - np.nanmin(arr) + 1e-6) - 1

        w_scaled = scale_to_range(w)
        x_scaled = scale_to_range(x)
        y_scaled = scale_to_range(y)
        z_scaled = scale_to_range(z)

        norm_factor = (x_scaled**2 + y_scaled**2 + w_scaled**2 + z_scaled**2) ** (1/2)
        return norm_factor

class CookedReturn:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Metric.get_columns(live)

        def scale_to_range(arr):
            return 2 * (arr - np.nanmin(arr)) / (np.nanmax(arr) - np.nanmin(arr) + 1e-6) - 1
        
        w = winsorize(price["dividend"].rolling(window=timeframe).mean().bfill().values, [0.01, 0.01])
        x = winsorize((price[cols["price"]] * price[cols["volume"]]).rolling(window=timeframe).mean().bfill(), [0.01, 0.01])
        y = winsorize(price[cols["price"]].pct_change().rolling(window=timeframe).std().bfill(), [0.01, 0.01])
        z = winsorize(price[cols["price"]].pct_change().rolling(window=timeframe).mean().bfill(), [0.01, 0.01])
        
        x_scaled = scale_to_range(x) * 100
        norm_factor = (1 + w) * (1 - y) * (1 + z) * x_scaled
        return norm_factor  

class MarketCap:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Metric.get_columns(live)
        return (price[cols["price"]] * price[cols["volume"]])

class Dividend:
    @staticmethod
    def calculate(price, timeframe, live):
        return price["dividend"].ffill().fillna(0).rolling(window=timeframe).mean()

class PriceToReturn:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Metric.get_columns(live)
        return price[cols["price"]].rolling(window=timeframe).mean() / price[cols["price"]].pct_change(5).rolling(window=timeframe).mean() * 100