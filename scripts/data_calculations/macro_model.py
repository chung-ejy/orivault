from database.adatabase import ADatabase
import pandas as pd
from processor.processor import Processor as processor
from xgboost import XGBRegressor
import numpy as np
import warnings
warnings.simplefilter(action="ignore")

fred = ADatabase("fred")
factors = ["market_yield","sp500","oil"
        #    ,"gdp","inflation","m2"
           ]
fred.connect()

spy = fred.retrieve("sp500")
spy = spy.rename(columns={"value":"spy"})
spy["spy"] = spy["spy"].replace(".",np.nan)
spy.dropna(inplace=True)
spy["spy"] = [float(x) for x in spy["spy"]]
spy = processor.column_date_processing(spy)
spy["year"] = [x.year for x in spy["date"]]

for factor in factors:
    factor_df = fred.retrieve(factor)
    factor_df = factor_df.rename(columns={"value":factor})
    factor_df[factor] = factor_df[factor].replace(".",np.nan)
    factor_df.dropna(inplace=True)
    factor_df[factor] = [float(x) for x in factor_df[factor]]
    factor_df = processor.column_date_processing(factor_df)
    factor_df["year"] = [x.year for x in factor_df["date"]]
    spy = spy.merge(factor_df[["date",factor]],on="date",how="left")
fred.disconnect()

spy = spy.rename(columns={"spy":"y"})
spy["y"] = spy["y"].shift(-60)
training_data = spy[spy["year"]<2020].dropna()
model = XGBRegressor()
model.fit(training_data[factors],training_data["y"])
sim = spy[spy["year"]>=2019]
sim["prediction"] = model.predict(sim[factors])

fred.connect()
fred.drop("sp500_projections")
fred.store("sp500_projections",sim[["date","sp500","prediction"]])
fred.disconnect()