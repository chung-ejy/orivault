class KPI:
    @staticmethod
    def performance(trades, portfolio, rolling_window=10):
        """
        Calculate performance metrics for a trading strategy.

        Parameters:
        - trades (DataFrame): DataFrame containing trade-level data with required columns:
                              ['return', 'date'].
        - portfolio (DataFrame): DataFrame containing portfolio-level data with required columns:
                                 ['pnl', 'benchmark_pnl'].
        - rolling_window (int): Rolling window size for volatility and downside metrics.
        
        Returns:
        - dict: Dictionary containing calculated performance metrics.
        """

        # Validate input DataFrames
        required_trades_cols = ["return", "date"]
        required_portfolio_cols = ["pnl", "benchmark_pnl"]

        if not all(col in trades.columns for col in required_trades_cols):
            raise KeyError(f"Trades DataFrame missing required columns: {required_trades_cols}")
        if not all(col in portfolio.columns for col in required_portfolio_cols):
            raise KeyError(f"Portfolio DataFrame missing required columns: {required_portfolio_cols}")

        # Performance metrics
        pnl = portfolio[portfolio["date"]==portfolio["date"].max()]["pnl"].iloc[0] 
         # Final portfolio profit/loss
        raw_pnl = portfolio[portfolio["date"]==portfolio["date"].max()]["raw_pnl"].iloc[0]
        benchmark_pnl = portfolio[portfolio["date"]==portfolio["date"].max()]["benchmark_pnl"].iloc[0]
        downside = portfolio["return"].min()  # Maximum downside deviation
        portfolio_std = portfolio["pnl"].std()  # Overall portfolio volatility
        portfolio_std = 1e-6 if portfolio_std == 0 else portfolio_std  # Prevent division by zero
        # Outperformance ratio
        sharpe_ratio = (pnl -benchmark_pnl ) / portfolio_std
        tracking_error = (portfolio["pnl"]-portfolio["benchmark_pnl"]).std()
        information_ratio = (pnl -benchmark_pnl ) / tracking_error
        # Compile metrics into a dictionary
        metrics = {
            "date": trades["date"].max(),  # Latest trade date
            "pnl": pnl,
            "raw_pnl": raw_pnl,
            "downside": downside,
            "coefficient_of_variation": pnl/portfolio_std,
            "portfolio_std": portfolio_std,  
            "sharpe_ratio": sharpe_ratio,
            "tracking_error":tracking_error,
            "information_ratio":information_ratio
        }

        return metrics