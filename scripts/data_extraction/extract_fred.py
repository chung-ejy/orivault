from common.extractor.fred_extractor import FREDExtractor
from datetime import datetime, timedelta
from common.database.adatabase import ADatabase

## Define classes and constants
fred = ADatabase("fred")
start = datetime.now() - timedelta(days=365.25*14)
end = datetime.now()

## download macro factors
sp500 = FREDExtractor.sp500(start,end)
market_yield = FREDExtractor.market_yield(start,end)
oil = FREDExtractor.oil(start,end)
gdp = FREDExtractor.gdp(start,end)
m2 = FREDExtractor.m2(start,end)
inflation = FREDExtractor.inflation(start,end)

## store macro factors and reset databases
fred.connect()
fred.drop("sp500")
fred.drop("market_yield")
fred.store("sp500",sp500)
fred.store("market_yield",market_yield)
fred.drop("oil")
fred.store("oil",oil)
fred.drop("gdp")
fred.store("gdp",gdp)
fred.drop("m2")
fred.store("m2",m2)
fred.drop("inflation")
fred.store("inflation",inflation)
fred.disconnect()