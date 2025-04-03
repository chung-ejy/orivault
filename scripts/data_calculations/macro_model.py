from common.database.adatabase import ADatabase
from common.processor.processor import Processor as processor
from xgboost import XGBRegressor
import numpy as np

## Define classes and constants
fred = ADatabase("fred")
factors = ["market_yield","sp500","oil","gdp","inflation","m2"]

## Create Macro Model
fred.connect()
spy = fred.retrieve("sp500")
spy = spy.rename(columns={"value":"spy"})
spy["spy"] = spy["spy"].replace(".",np.nan)
spy.dropna(inplace=True)
spy["spy"] = [float(x) for x in spy["spy"]]
spy = processor.lower_column(spy)
spy = processor.utc_date(spy)
spy["year"] = [x.year for x in spy["date"]]

## Query Macro Factors
for factor in factors:
    factor_df = fred.retrieve(factor)
    factor_df = factor_df.rename(columns={"value":factor})
    factor_df[factor] = factor_df[factor].replace(".",np.nan)
    factor_df.dropna(inplace=True)
    factor_df[factor] = [float(x) for x in factor_df[factor]]
    factor_df = processor.lower_column(factor_df)
    factor_df = processor.utc_date(factor_df)
    factor_df["year"] = [x.year for x in factor_df["date"]]
    spy = spy.merge(factor_df[["date",factor]],on="date",how="left")
fred.disconnect()

## Fit Model
spy = spy.rename(columns={"spy":"y"})
spy["y"] = spy["y"].shift(-60)
training_data = spy[spy["year"]<2020].dropna()
model = XGBRegressor()
model.fit(training_data[factors],training_data["y"])
sim = spy[spy["year"]>=2019]
sim["prediction"] = model.predict(sim[factors])

## Store projections and forget model
fred.connect()
fred.drop("sp500_projections")
fred.store("sp500_projections",sim[["date","sp500","prediction"]])
fred.disconnect()