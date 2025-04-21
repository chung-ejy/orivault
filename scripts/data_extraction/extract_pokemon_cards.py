## PATH settings
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), ''))
sys.path.append(project_root)
COMMON_PATH = os.path.join(project_root, 'common')

from common.extractor.pokemontcg_extractor import PokemonTCGExtractor
from common.database.adatabase import ADatabase
from datetime import datetime, timezone
import pandas as pd

market = ADatabase("market")
pokemon = PokemonTCGExtractor()

cards = pokemon.cards()
cards_df = pd.DataFrame(cards)
cards_df.rename(columns={"market":"adjclose"},inplace=True)
cards_df["date"] = datetime.now(tz=timezone.utc)
market.connect()
market.store("pokemon",cards_df)
market.disconnect()