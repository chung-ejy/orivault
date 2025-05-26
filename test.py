from common.extractor.alpaca_extractor import AlpacaExtractor
from common.processor.utils import Utils
from datetime import timedelta

alp = AlpacaExtractor(paper=False)
print(alp.latest_trade("AAPL"))