import pandas as pd

from AnalyticsApp import StockAnalyticsApp

if __name__ == '__main__':
	preceding_days: int = 30
	peace_level: float = 0.2
	date: str = input ( "Select data from date YYYY-MM-DD:" )
	df: pd.DataFrame = pd.read_csv ( date + "-30D-Hist-Ashares.csv" )
	app: StockAnalyticsApp = StockAnalyticsApp ( df )
	app.mainloop ()
