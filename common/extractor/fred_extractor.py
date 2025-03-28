import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
import requests as r

# Purpose: This class facilitates interaction with the Federal Reserve Economic Data (FRED) API,
# allowing retrieval of various economic and financial datasets for analysis.
class FREDExtractor(object):
    
    # Purpose: Initializes the FREDExtractor instance and retrieves the API key from environment variables.
    def __init__(self):
        self.token = os.getenv("FREDKEY")

    # Purpose: Fetches 10-Year Treasury market yield observations within a specified date range.
    # Inputs:
    # - start (datetime): Start date of the observation period.
    # - end (datetime): End date of the observation period.
    # Returns:
    # - Pandas DataFrame containing the market yield observations.
    def market_yield(self, start, end):
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "api_key": self.token,
            "observation_start": start.strftime("%Y-%m-%d"),
            "observation_end": end.strftime("%Y-%m-%d"),
            "file_type": "json",
            "series_id": "DGS10"
        }
        requestBody = r.get(url, params=params)
        return pd.DataFrame(requestBody.json()["observations"])
    
    # Purpose: Fetches S&P 500 index observations within a specified date range.
    # Inputs:
    # - start (datetime): Start date of the observation period.
    # - end (datetime): End date of the observation period.
    # Returns:
    # - Pandas DataFrame containing the S&P 500 observations.
    def sp500(self, start, end):
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "api_key": self.token,
            "observation_start": start.strftime("%Y-%m-%d"),
            "observation_end": end.strftime("%Y-%m-%d"),
            "file_type": "json",
            "series_id": "SP500"
        }
        requestBody = r.get(url, params=params)
        return pd.DataFrame(requestBody.json()["observations"])
    
    # Purpose: Fetches inflation rate observations within a specified date range.
    # Inputs:
    # - start (datetime): Start date of the observation period.
    # - end (datetime): End date of the observation period.
    # Returns:
    # - Pandas DataFrame containing the inflation rate observations.
    def inflation(self, start, end):
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "api_key": self.token,
            "observation_start": start.strftime("%Y-%m-%d"),
            "observation_end": end.strftime("%Y-%m-%d"),
            "file_type": "json",
            "series_id": "FPCPITOTLZGUSA"
        }
        requestBody = r.get(url, params=params)
        return pd.DataFrame(requestBody.json()["observations"])
    
    # Purpose: Fetches crude oil price observations within a specified date range.
    # Inputs:
    # - start (datetime): Start date of the observation period.
    # - end (datetime): End date of the observation period.
    # Returns:
    # - Pandas DataFrame containing the crude oil price observations.
    def oil(self, start, end):
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "api_key": self.token,
            "observation_start": start.strftime("%Y-%m-%d"),
            "observation_end": end.strftime("%Y-%m-%d"),
            "file_type": "json",
            "series_id": "DCOILBRENTEU"
        }
        requestBody = r.get(url, params=params)
        return pd.DataFrame(requestBody.json()["observations"])
    
    # Purpose: Fetches GDP observations within a specified date range.
    # Inputs:
    # - start (datetime): Start date of the observation period.
    # - end (datetime): End date of the observation period.
    # Returns:
    # - Pandas DataFrame containing the GDP observations.
    def gdp(self, start, end):
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "api_key": self.token,
            "observation_start": start.strftime("%Y-%m-%d"),
            "observation_end": end.strftime("%Y-%m-%d"),
            "file_type": "json",
            "series_id": "GDPC1"
        }
        requestBody = r.get(url, params=params)
        return pd.DataFrame(requestBody.json()["observations"])
    
    # Purpose: Fetches M2 money supply observations within a specified date range.
    # Inputs:
    # - start (datetime): Start date of the observation period.
    # - end (datetime): End date of the observation period.
    # Returns:
    # - Pandas DataFrame containing the M2 money supply observations.
    def m2(self, start, end):
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "api_key": self.token,
            "observation_start": start.strftime("%Y-%m-%d"),
            "observation_end": end.strftime("%Y-%m-%d"),
            "file_type": "json",
            "series_id": "M2SL"
        }
        requestBody = r.get(url, params=params)
        return pd.DataFrame(requestBody.json()["observations"])