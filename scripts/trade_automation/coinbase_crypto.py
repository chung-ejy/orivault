## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from common.database.adatabase import ADatabase
from common.extractor.coinbase_extractor import CoinbaseExtractor  
import math
import pandas as pd
import re
from datetime import datetime
import uuid
import time

def generate_client_order_id(prefix: str = "order") -> str:
    """
    Generate a unique client_order_id for Coinbase Advanced API.
    
    Parameters:
        prefix (str): An optional prefix to identify the order type or purpose.
    
    Returns:
        str: A unique client_order_id.
    """
    # Use the current time in milliseconds
    timestamp = int(time.time() * 1000)
    
    # Generate a UUID4 string and take the first 8 characters
    unique_id = str(uuid.uuid4())[:8]
    
    # Combine prefix, timestamp, and unique identifier
    client_order_id = f"{prefix}_{timestamp}_{unique_id}"
    return client_order_id

if datetime.now().weekday() == 0:
    ori = ADatabase("ori")
    extractor = CoinbaseExtractor()

    ori.cloud_connect()
    recs = ori.retrieve("crypto_recommendations")
    top = ori.retrieve("crypto_results").to_dict("records")[0]
    ori.disconnect()

    # # closing
    portfolio_uuid = extractor.client.get_portfolios("DEFAULT")["portfolios"][0]["uuid"]
    portfolio = extractor.client.get_portfolio_breakdown(portfolio_uuid)
    positions = portfolio["breakdown"].spot_positions
    crypto_positions = [x for x in positions if x.asset != "USD" ]
    for crypto_position in crypto_positions:
        amount = float(crypto_position.available_to_trade_crypto)
        ticker = crypto_position.asset + "-USD"
        print("sell",ticker,amount)
        sell_order_id = generate_client_order_id()
        extractor.client.market_order_sell(client_order_id=sell_order_id,product_id=ticker,base_size=str(amount))

    # ## purchasing
    portfolio = extractor.client.get_portfolio_breakdown(portfolio_uuid)
    positions = portfolio["breakdown"].spot_positions
    cash_position = [x for x in positions if x.asset == "USD" ][0]
    cash = float(cash_position.available_to_trade_crypto)

    for row in recs.iterrows():
        ticker = row[1]["ticker"]
        allocation = round(cash*row[1]["weight"],2) if top["allocation_type"] != "equal" else round(cash/recs.index.size,2)
        buy_order_id = generate_client_order_id()
        if row[1]["position_type"] == 1:
            extractor.client.market_order_buy(client_order_id=buy_order_id,product_id=ticker,quote_size=str(allocation))
        else:
            extractor.client.market_order_sell(client_order_id=buy_order_id,product_id=ticker,quote_size=str(allocation))