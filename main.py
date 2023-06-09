import pandas as pd

import a_share_utils
from AnalyticsApp import StockAnalyticsApp

if __name__ == '__main__':
	preceding_days: int = 30
	peace_level: float = 0.2
	df: pd.DataFrame = a_share_utils.get_a_share_hist_data ( preceding_days = preceding_days , peace_level = peace_level )
	app: StockAnalyticsApp = StockAnalyticsApp ( df )
	app.mainloop ()
