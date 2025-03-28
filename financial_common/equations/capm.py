
class CAPM(object):
    
    @staticmethod
    def apply(df):
        df["expected_return"] = (df["prediction"] - df["adjclose"]) / df["adjclose"]
        df["historical_return"] = df["adjclose"].pct_change(60)
        df["factor_return"] = (df["sp500_prediction"] - df["sp500"]) / df["sp500"]
        df["cov"] = df["factor_return"].rolling(100).cov(df["expected_return"])
        df["market_cov"] = df["cov"]
        df["var"] = df["factor_return"].rolling(100).var()
        df["beta"] = df["cov"] / df["var"]
        df["factor"] = df["rf"] + df["beta"] * (df["expected_return"] - df["rf"])
        df["risk"] = df["adjclose"].rolling(100).var()
        df["sigma"] = df["adjclose"].rolling(262).std()
        drop_cols = ["expected_return","historical_return","factor_return"
                     ,"cov","market_cov","var","beta","prediction","sp500_prediction","sp500"]
        return df.drop(drop_cols,axis=1)   
