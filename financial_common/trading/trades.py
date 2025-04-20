class Trades(object):

    @staticmethod
    def timeframe_trades(sim,timeframe="week",factor="factor",group="sic_description",risk="risk",additional_columns=[]):
        sim["sell_price"] = sim["adjclose"]
        sim["sell_date"] = sim["date"]
        query = {"date":"last","adjclose":"first","sell_price":"last",group:"first"}
        query[factor] = "first"
        query[group] = "first"
        query[risk.label] = "first"
        for additional_column in additional_columns:
            query[additional_column] = "first"
        timeframe_sim = sim.groupby(["year",timeframe,"ticker"]).agg(query).reset_index().sort_values("date")
        if timeframe=="week":
            timeframe_sim = timeframe_sim[(timeframe_sim[timeframe] != 1) & (timeframe_sim[timeframe] < 52)].sort_values("date")
        return timeframe_sim