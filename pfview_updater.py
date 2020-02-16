import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG, filename="portfolio.log", filemode="a")
logger = logging.getLogger()

import backend.portfolio_view as portfolio
import pandas as pd

# In case of need to rebuild the whole portfolio view, execute
# portfolio.Rebuild_PortfolioView()

logger.info("Updating Portfolio View Table")

portfolio.UpdatePortfolioView()


