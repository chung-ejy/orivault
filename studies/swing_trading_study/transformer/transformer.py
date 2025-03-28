from indicator.indicator import Indicator
class Transformer(object):

    @staticmethod
    def transform(sim):
        query = {"date":"last","adjclose":"first","sell_price":"last","market_cap":"first"}
        signals = Indicator.get_trading_signals()
        for col in signals:
            query[col] = "first"
        weekly_sim = sim.groupby(["year","week","ticker"]).agg(query).reset_index().sort_values("date")
        weekly_sim["y"] = weekly_sim["sell_price"] / weekly_sim["adjclose"]
        weekly_sim[f"market_cap_rank"] = weekly_sim.groupby(["year","week"])["market_cap"].rank(ascending=False,pct=True)
        product = weekly_sim[(weekly_sim["week"] != 1) & (weekly_sim["week"] < 52)].sort_values("date")
        return product