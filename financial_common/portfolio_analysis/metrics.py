
class Metrics(object):

    @staticmethod
    def performance(self,trades,portfolio):
        # Performance metrics
        pnl = portfolio["pnl"].iloc[-1]
        rolling_max = portfolio["pnl"].rolling(10).max()
        downside = (portfolio["pnl"] / rolling_max).min(skipna=True)
        rolling_std = portfolio["pnl"].rolling(10).std()
        rolling_mean = portfolio["pnl"].rolling(10).mean()
        coev = (rolling_std / rolling_mean).mean(skipna=True)
        std = portfolio["pnl"].std()
        std = 1e-6 if std == 0 else std
        wins = trades["return"] >= 1
        average_gain = trades.loc[wins, "return"].mean()
        average_loss = trades.loc[~wins, "return"].mean()
        win_rate = wins.sum() / len(trades)
        weekly_return = win_rate * average_gain + (1 - win_rate) * average_loss
        outperformance_ratio = (pnl - portfolio["benchmark_pnl"].iloc[-1]) / std

        metrics = {
            "date": trades["date"].max(),
            "pnl": pnl,
            "downside": downside,
            "coev": coev,
            "std": std,
            "average_gain": average_gain,
            "average_loss": average_loss,
            "w/l": win_rate,
            "weekly_return": weekly_return,
            "outperformance_ratio": outperformance_ratio
        }
        return metrics