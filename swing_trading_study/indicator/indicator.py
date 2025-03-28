import numpy as np

class Indicator(object):

        
    @staticmethod
    def calculate_indicators(price,timeframe=100,live=False):
        """
        Calculate technical indicators, classifying them as positive (boosting score) or negative (taxing score).
        Aggregates them into a weighted 'rogan' score.
        """
        if live:
            cols = {
                "price": "adjclose",
                "high": "high",
                "low": "low",
                "volume": "volume"
            }
        else:
            cols = {
                "price": "reference_price",
                "high": "reference_high",
                "low": "reference_low",
                "volume": "reference_volume"
            }
            price[cols["price"]] = price["adjclose"].shift(1)
            price[cols["volume"]] = price["volume"].shift(1)
            price[cols["high"]] = price["high"].shift(1)
            price[cols["low"]] = price["low"].shift(1)
        # Core calculations
        price["adr"] = ((price[cols["high"]] - price[cols["low"]]) / price[cols["price"]]).rolling(timeframe).mean()
        price["sma"] = price[cols["price"]].rolling(timeframe).mean() / price[cols["price"]]
        price["ema"] = price[cols["price"]].ewm(span=timeframe, adjust=False).mean() / price[cols["price"]]

        delta = price[cols["price"]].diff()
        gain = delta.where(delta > 0, 0).rolling(timeframe).sum()
        loss = -delta.where(delta < 0, 0).rolling(timeframe).sum()

        rolling_mean = price[cols["price"]].rolling(timeframe).mean()
        price["std"] = price[cols["price"]].rolling(timeframe).std()
        price["bollinger_upper"] = (rolling_mean + 2 * price["std"]) / price[cols["price"]]
        price["bollinger_lower"] = (rolling_mean - 2 * price["std"]) / price[cols["price"]]

        price["pct_change"] = price[cols["price"]] / price[cols["price"]].shift(100)
        price["coev"] = price["std"] / rolling_mean
        price["market_cap"] = (price[cols["price"]] * price[cols["volume"]]).rolling(window=timeframe).mean()
        price["atr"] = (price[cols["high"]] - price[cols["low"]]).rolling(timeframe).mean()

        # Momentum Indicators
        price["momentum"] = price[cols["price"]].diff(timeframe)
        price["roc"] = price[cols["price"]].pct_change(timeframe)

        # Williams %R (reverse scaling so that high values are positive)
        price["williams_r"] = -((price[cols["high"]].rolling(timeframe).max() - price[cols["price"]]) /
                                (price[cols["high"]].rolling(timeframe).max() - price[cols["low"]].rolling(timeframe).min())) * 100

        # On-Balance Volume (OBV)
        price["obv"] = (np.sign(price[cols["price"]].diff()) * price[cols["volume"]]).cumsum()

        # VWAP (Volume Weighted Average Price)
        price["vwap"] = (price[cols["price"]] * price[cols["volume"]]).cumsum() / price[cols["volume"]].cumsum()

        # Market Impact Index
        price["market_impact"] = price["adr"] * price[cols["volume"]]

        # **SEPARATE BOOSTING & PENALIZING INDICATORS**
        boosting_indicators = {
            "sma": 0.1, "ema": 0.1, "bollinger_upper": 0.05, "momentum": 0.15, 
            "roc": 0.15, "obv": 0.1, "vwap": 0.05, "market_impact": 0.1
        }
        
        penalizing_indicators = {
            "bollinger_lower": -0.05, "coev": -0.1, "williams_r": -0.1
        }

        # Compute weighted sum for `rogan`
        price["rogan"] = sum(price[ind] * weight for ind, weight in boosting_indicators.items() if ind in price) + \
                        sum(price[ind] * weight for ind, weight in penalizing_indicators.items() if ind in price)

        return price.dropna()

    
    def get_trading_signals():
        return [
            "adr",  # Average Daily Range
            "sma",  # Simple Moving Average Ratio
            "ema",  # Exponential Moving Average Ratio
            "bollinger_upper",  # Upper Bollinger Band Ratio
            "bollinger_lower",  # Lower Bollinger Band Ratio
            "pct_change",  # Percentage Change Over 100 Days
            "coev",  # Coefficient of Variation
            "market_impact",  # ADR * Volume
            "atr",  # Average True Range
            "momentum",  # Momentum Indicator
            "roc",  # Rate of Change
            "williams_r",  # Williams %R (Overbought/Oversold)
            "obv",  # On-Balance Volume
            "vwap",  # Volume Weighted Average Price
            "rogan",  # Aggregated Trading Signal Score
        ]