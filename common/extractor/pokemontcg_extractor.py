import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
from pokemontcgsdk import RestClient
from pokemontcgsdk import Card

# Purpose: This class interacts with the Tiingo API to retrieve historical price data for specific stock tickers.
class PokemonTCGExtractor(object):

    # Purpose: Initializes the TiingoExtractor instance and retrieves the API token from environment variables.
    def __init__(self):
        RestClient.configure(os.getenv("POKEMONTCGKEY"))
    
    def cards(self):
        cards = Card.where(q="legalities.standard:legal")
        prices = []
        for card in cards:
            try:
                price = card.tcgplayer.prices.normal.__dict__
                price["ticker"] = card.name
                price["rarity"] = card.rarity
                prices.append(price)
            except Exception as e:
                continue
        return prices