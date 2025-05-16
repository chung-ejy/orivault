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
        pnl = portfolio[portfolio["date"]==portfolio["date"].max()]["pnl"].iloc[0]  # Final portfolio profit/loss
        benchmark_pnl = portfolio[portfolio["date"]==portfolio["date"].max()]["benchmark_pnl"].iloc[0]
        rolling_max = portfolio["pnl"].rolling(rolling_window).max()  # Rolling maximum
        downside = (portfolio["pnl"] / rolling_max).min(skipna=True)  # Maximum downside deviation
        rolling_std = portfolio["pnl"].rolling(rolling_window).std()  # Rolling volatility
        rolling_mean = portfolio["pnl"].rolling(rolling_window).mean()  # Rolling mean return
        coefficient_of_variation = (rolling_std / rolling_mean).mean(skipna=True)  # Coefficient of variation
        portfolio_std = portfolio["pnl"].std()  # Overall portfolio volatility
        portfolio_std = 1e-6 if portfolio_std == 0 else portfolio_std  # Prevent division by zero

        # Trade-level metrics
        wins = trades["return"] >= 1  # Successful trades
        average_gain = trades.loc[wins, "return"].mean()  # Average gain from winning trades
        average_loss = trades.loc[~wins, "return"].mean()  # Average loss from losing trades
        win_rate = wins.sum() / len(trades)  # Win rate (successful trades / total trades)

        # Weekly return
        weekly_return = win_rate * average_gain + (1 - win_rate) * average_loss

        # Outperformance ratio
        sharpe_ratio = (pnl -benchmark_pnl ) / portfolio_std

        # Compile metrics into a dictionary
        metrics = {
            "date": trades["date"].max(),  # Latest trade date
            "pnl": pnl,
            # "downside": downside,
            "coefficient_of_variation": pnl/portfolio_std,
            "portfolio_std": portfolio_std,
            "average_gain": average_gain,
            "average_loss": average_loss,
            "win_loss_ratio": win_rate,
            "weekly_return": weekly_return,
            "sharpe_ratio": sharpe_ratio
        }

        return metrics