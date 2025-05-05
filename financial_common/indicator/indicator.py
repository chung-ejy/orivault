from enum import Enum
import numpy as np

class Indicator(Enum):
    ROLLING_DOLLAR_VOLUME = ("rolling_dollar_volume", lambda: RollingDollarVolume())
    ADR = ("adr", lambda: ADRIndicator())
    SMA = ("sma", lambda: SMAIndicator())
    EMA = ("ema", lambda: EMAIndicator())
    BOLLINGER_UPPER = ("bollinger_upper", lambda: BollingerUpperIndicator())
    BOLLINGER_LOWER = ("bollinger_lower", lambda: BollingerLowerIndicator())
    MOMENTUM = ("momentum", lambda: MomentumIndicator())
    ROC = ("roc", lambda: ROCIndicator())
    WILLIAMS_R = ("williams_r", lambda: WilliamsRIndicator())
    OBV = ("obv", lambda: OBVIndicator())
    VWAP = ("vwap", lambda: VWAPIndicator())
    MARKET_IMPACT = ("market_impact", lambda: MarketImpactIndicator())
    ATR = ("atr", lambda: ATRIndicator())

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

# Updated individual indicator classes
class RollingDollarVolume:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return (price[cols["price"]] * price[cols["volume"]]).rolling(window=timeframe).mean()

class ADRIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return ((price[cols["high"]] - price[cols["low"]]) / price[cols["price"]]).rolling(timeframe).mean()

class SMAIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return price[cols["price"]].rolling(timeframe).mean() / price[cols["price"]]

class EMAIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return price[cols["price"]].ewm(span=timeframe, adjust=False).mean() / price[cols["price"]]

class BollingerUpperIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        rolling_mean = price[cols["price"]].rolling(timeframe).mean()
        std_dev = price[cols["price"]].rolling(timeframe).std()
        return (rolling_mean + 2 * std_dev) / price[cols["price"]]

class BollingerLowerIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        rolling_mean = price[cols["price"]].rolling(timeframe).mean()
        std_dev = price[cols["price"]].rolling(timeframe).std()
        return (rolling_mean - 2 * std_dev) / price[cols["price"]]

class MomentumIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return price[cols["price"]].diff(timeframe)

class ROCIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return price[cols["price"]].pct_change(timeframe, fill_method=None)

class WilliamsRIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return -((price[cols["high"]].rolling(timeframe).max() - price[cols["price"]]) /
                 (price[cols["high"]].rolling(timeframe).max() - price[cols["low"]].rolling(timeframe).min())) * 100

class OBVIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return (np.sign(price[cols["price"]].diff()) * price[cols["volume"]]).rolling(timeframe).sum()

class VWAPIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return (price[cols["price"]] * price[cols["volume"]]).rolling(timeframe).sum() / price[cols["volume"]].rolling(timeframe).sum()

class MarketImpactIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        adr = ADRIndicator.calculate(price, timeframe, live)
        return adr * price[cols["volume"]]

class ATRIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return (price[cols["high"]] - price[cols["low"]]).rolling(timeframe).mean()