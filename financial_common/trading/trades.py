from financial_common.indicator.indicator import Indicator

class Trades(object):

    @staticmethod
    def timeframe_trades(sim,timeframe="week",group="rolling_dollar_volume"):
        query = {"date":"last","adjclose":"first","sell_price":"last",group:"first"}
        signals = Indicator.get_trading_signals()
        for col in signals:
            query[col] = "first"
        timeframe_sim = sim.groupby(["year",timeframe,"ticker"]).agg(query).reset_index().sort_values("date")
        timeframe_sim["y"] = timeframe_sim["sell_price"] / timeframe_sim["adjclose"]
        timeframe_sim[f"{group}_rank"] = timeframe_sim.groupby(["year",timeframe])[group].rank(ascending=False,pct=True)
        if timeframe=="week":
            timeframe_sim = timeframe_sim[(timeframe_sim[timeframe] != 1) & (timeframe_sim[timeframe] < 52)].sort_values("date")
        return timeframe_sim