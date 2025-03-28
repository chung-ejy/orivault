
class FactorLoading(object):
    
    @staticmethod
    def apply(df,y_variable,x_variable,window):
        df["cov"] = df[y_variable].rolling(window).cov(df[x_variable])
        df["var"] = df[x_variable].rolling(window).var()
        df["beta"] = df["cov"] / df["var"]
        df[f"{y_variable}_prediction"] = df["beta"] * df[y_variable]
        return df