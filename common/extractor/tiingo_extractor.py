import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
import requests as r

# Purpose: This class interacts with the Tiingo API to retrieve historical price data for specific stock tickers.
class TiingoExtractor(object):

    # Purpose: Initializes the TiingoExtractor instance and retrieves the API token from environment variables.
    def __init__(self):
        self.token = os.getenv("TIINGOKEY")

    # Purpose: Fetches historical daily price data for a specific stock ticker within the given date range.
    # Inputs:
    # - ticker (str): The stock ticker symbol (e.g., "AAPL" for Apple).
    # - start (datetime): Start date of the observation period.
    # - end (datetime): End date of the observation period.
    # Returns:
    # - Pandas DataFrame containing the historical price data retrieved from the Tiingo API.
    @classmethod
    def prices(self, ticker, start, end):
        params = {
            "token": self.token,
            "startDate": start.strftime("%Y-%m-%d"),
            "endDate": end.strftime("%Y-%m-%d"),
            "format": "json",
            "resampleFreq": "daily"
        }
        url = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices/"
        requestBody = r.get(url, params=params)
        return pd.DataFrame(requestBody.json())