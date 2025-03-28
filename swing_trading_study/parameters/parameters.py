from indicator.indicator import Indicator
from market_constants.market_constants import *
class Parameters(object):

    @staticmethod
    def generate_parameters():
        signals = Indicator.get_trading_signals()
        parameters = []
        for signal in signals:
            for ascending in ascendings:
                for direction in directions:
                        parameters.append({
                            "stoploss":stoploss,
                            "filter_rate":filter_rate,
                            "signal": signal,
                            "ascending": ascending,
                            "direction": direction
                        })
        param_bounds = {
            'num_stocks': (min(num_stocks), max(num_stocks)),
        }
        return param_bounds,parameters
    
    @staticmethod
    def generate_bruteforce_parameters():
        parameters = []
        signals = Indicator.get_trading_signals()
        for stocks in num_stocks: 
            for signal in signals:
                for ascending in ascendings:
                    for direction in directions:
                            parameters.append({
                                "stoploss":stoploss,
                                "filter_rate":filter_rate,
                                "signal": signal,
                                "ascending": ascending,
                                "direction": direction,
                                'market_cap_ceiling': ceiling,
                                'market_cap_floor': floor,
                                'num_stocks': stocks,
                            })
        return parameters