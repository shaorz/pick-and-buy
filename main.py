import pandas as pd

import a_share_utils
from AnalyticsApp import StockAnalyticsApp

if __name__ == '__main__':
	preceding_days: int = 30
	peace_level: float = 0.2
	a_share_data , volume_benchmark_df = a_share_utils.get_a_share_hist_data ( preceding_days = preceding_days , peace_level = peace_level )

	df: pd.DataFrame = pd.read_csv ( "Analytics-2023-03-29-30D-Hist-Ashares.csv" )
	app: StockAnalyticsApp = StockAnalyticsApp ( df )
	app.start_app ()

# scrollbar for peacelevel
