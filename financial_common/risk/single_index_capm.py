class SingleIndexCAPM:
    
    @staticmethod
    def apply(df, rolling_window_beta=100, rolling_window_sigma=262):
        """
        Apply CAPM-related computations to the given DataFrame.
        
        Parameters:
        - df (DataFrame): The input data containing required columns.
        - rolling_window_beta (int): Rolling window size for beta and risk computations.
        - rolling_window_sigma (int): Rolling window size for standard deviation (sigma) computations.
        
        Returns:
        - DataFrame: Processed DataFrame with final computations applied.
        """

        df["expected_return"] = (df["prediction"] - df["adjclose"]) / df["adjclose"]
        df["historical_return"] = df["adjclose"].pct_change(60)
        df["factor_return"] = (df["sp500_prediction"] - df["sp500"]) / df["sp500"]
        df["cov"] = df["factor_return"].rolling(rolling_window_beta).cov(df["expected_return"])
        df["market_cov"] = df["cov"]
        df["var"] = df["factor_return"].rolling(rolling_window_beta).var()
        df["beta"] = df["cov"] / df["var"]
        df["factor"] = df["rf"] + df["beta"] * (df["expected_return"] - df["rf"])
        df["risk"] = df["adjclose"].rolling(rolling_window_beta).var()
        df["sigma"] = df["adjclose"].rolling(rolling_window_sigma).std()
        drop_cols = [
            "expected_return", "historical_return", "factor_return",
            "cov", "market_cov", "var", "beta", "prediction",
            "sp500_prediction", "sp500"
        ]
        return df.drop(drop_cols, axis=1)