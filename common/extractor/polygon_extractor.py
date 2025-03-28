import requests as r
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
# Purpose: This class provides methods for interacting with the Polygon.io API 
# to retrieve financial data, such as stock ticker information.
class PolygonExtractor(object):
    
    # Purpose: Initializes the PolygonExtractor instance with an API key for authentication.
    def __init__(self):
        self.key = os.getenv("POLYGONKEY")
        
    # Purpose: Retrieves information on stock tickers, including active common stocks (CS),
    # sorted and filtered as specified in the API call.
    # Returns:
    # - A JSON object containing stock ticker information retrieved from the Polygon.io API.
    def ticker_info(self):
        url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&type=CS&active=true&order=asc&limit=1000&sort=ticker&apiKey={self.key}"
        requestBody = r.get(url)
        data = requestBody.json()
        return data