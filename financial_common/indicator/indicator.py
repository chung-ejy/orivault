from enum import Enum
import numpy as np

class Indicator(Enum):
    OPTIMAL = ("optimal", lambda: OptimalIndicator())
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
    VOLUME_PRICE = ("volume_price",lambda:VolumePrice())

    def __init__(self, label, calculation_method):
        self.label = label
        self.calculation_method = calculation_method

    def calculate(self, price, timeframe=100, live=False):
        """Calculate reference values, add computed indicator values to the dataframe, and return the updated dataframe."""
        price = price.sort_values(by=["date"], ascending=True)
        for col in ["adjclose", "high", "low", "volume"]:
            price[f"{col}_test"] = price[col].shift(1)       
        price[self.label] = self.calculation_method().calculate(price, timeframe, live)
        return price

    @classmethod
    def get_columns(cls, live):
        """Return column mappings based on live or test mode."""
        return {
            "price": "adjclose" if live == True else "adjclose_test",
            "high": "high" if live == True else "high_test",
            "low": "low" if live == True else "low_test",
            "volume": "volume" if live == True else "volume_test"
        }

    @classmethod
    def indicator_type_factory(cls, indicator_type):
        mapping = {member.label: member for member in cls}
        return mapping.get(indicator_type, None)

    def __str__(self):
        return self.label

class OptimalIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return price[cols["price"]].pct_change(-5, fill_method=None)

class ADRIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return ((price[cols["high"]] - price[cols["low"]]) / price[cols["price"]]).rolling(timeframe).mean()

class SMAIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return price[cols["price"]].rolling(timeframe).mean() / price[cols["price"]] - 1


class EMAIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        return price[cols["price"]].ewm(span=timeframe, adjust=False).mean() / price[cols["price"]] -1
    
class SMACorrIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        rollings = (price[cols["price"]].rolling(timeframe).mean() / price[cols["price"]] - 1)
        rollings_corr = rollings.rolling(timeframe).corr(price[cols["price"]]) / rollings.rolling(timeframe).corr(price[cols["price"]]).abs()
        spread = 1 - (price[cols["high"]] - price[cols["low"]]).rolling(timeframe).mean() / price[cols["price"]].rolling(timeframe).mean()
        rollings_corr.replace([np.inf, -np.inf], np.nan, inplace=True)
        rollings_corr.fillna(0, inplace=True)
        return rollings * rollings_corr * spread

class EMACorrIndicator:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        rollings = (price[cols["price"]].ewm(span=timeframe, adjust=False).mean() / price[cols["price"]])
        rollings_corr = rollings.rolling(timeframe).corr(price[cols["price"]]) / rollings.rolling(timeframe).corr(price[cols["price"]]).abs()
        spread = 1 - (price[cols["high"]] - price[cols["low"]]).rolling(timeframe).mean() / price[cols["price"]].rolling(timeframe).mean()
        rollings_corr = rollings_corr.replace([np.inf, -np.inf], np.nan)
        rollings_corr = rollings_corr.fillna(0)
        risk = 1 - price[cols["price"]].pct_change().rolling(timeframe).mean()
        change = price[cols["price"]].pct_change()
        corr = change.shift(1).rolling(timeframe).corr(change) / change.shift(1).rolling(timeframe).corr(change).abs() 
        vtc = (price[cols["volume"]] / price[cols["price"]]).pct_change()
        return vtc

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
        return (price[cols["price"]] / price[cols["price"]].shift(1)) - 1

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
    
class VolumeReturn:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        ewm = price[cols["price"]].ewm(span=timeframe, adjust=False).mean() / price[cols["price"]]
        corr = ewm.rolling(timeframe).corr(price[cols["price"]]) / ewm.rolling(timeframe).corr(price[cols["price"]]).abs()
        market_cap = (price[cols["price"]].rolling(timeframe).mean() * price[cols["volume"]].rolling(timeframe).mean())
        return ewm / market_cap * 1000000

class VolumePrice:
    @staticmethod
    def calculate(price, timeframe, live):
        cols = Indicator.get_columns(live)
        spread = 1 - (price[cols["high"]] - price[cols["low"]]) / price[cols["price"]]
        volume = price[cols["volume"]]/1000000
        return spread * volume