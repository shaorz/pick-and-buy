# -*- coding: utf-8 -*-

import json
from datetime import datetime
from typing import Iterable , List , Mapping

import easyquotation
import pandas as pd
import requests
from progressbar import *


def get_stock_pool_today ( agent: str = 'tencent' , withPrefix: bool = True ) -> Mapping:
	"""
	:arg
	agent
	use sina for 新浪免费行情获取
	use jsl for 集思路的分级A数据
	use qq/tencent for 腾讯免费行情获取
	use boc for 中行美元最新汇率
	use timekline for 腾讯免费行情获取
	use daykline for 腾讯免费行情获取
	use hkquote for 腾讯免费行情获取 r_hk00981
	withPrefix 参数指定返回的行情字典中的股票代码 key 是否带 sz/sh 前缀
	:return:
	real time market data feed as a DataFrame
	"""
	quotation = easyquotation.use ( agent )
	df = quotation.market_snapshot ( prefix = withPrefix )
	return df


# 腾讯日线
def get_price_day_tx ( code: str , end_date: str = '' , count: int = 10 , frequency: str = '1d' ) -> pd.DataFrame:
	unit = 'week' if frequency in '1w' else 'month' if frequency in '1M' else 'day'
	if end_date:  end_date = end_date.strftime ( '%Y-%m-%d' ) if isinstance ( end_date , datetime.date ) else \
		end_date.split ( ' ' ) [ 0 ]
	end_date = '' if end_date == datetime.datetime.now ().strftime ( '%Y-%m-%d' ) else end_date
	URL = f'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},{unit},,{end_date},{count},qfq'
	st = json.loads ( requests.get ( URL ).content )
	ms = 'qfq' + unit
	stk = st [ 'data' ] [ code ]
	buf = stk [ ms ] if ms in stk else stk [ unit ]
	df = pd.DataFrame ( buf , columns = [ 'time' , 'open' , 'close' , 'high' , 'low' , 'volume' ] )
	df.time = pd.to_datetime ( df.time )
	df.set_index ( [ 'time' ] , inplace = True )
	df.index.name = ''
	return df


def get_price_min_tx ( code: str , end_date: str = None , count: int = 10 , frequency: str = '1d' ) -> pd.DataFrame:
	ts = int ( frequency [ :-1 ] ) if frequency [ :-1 ].isdigit () else 1
	if end_date: end_date = end_date.strftime ( '%Y-%m-%d' ) if isinstance ( end_date , datetime.date ) else \
		end_date.split ( ' ' ) [ 0 ]
	URL = f'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={code},m{ts},,{count}'
	st = json.loads ( requests.get ( URL ).content )
	buf = st [ 'data' ] [ code ] [ 'm' + str ( ts ) ]
	df = pd.DataFrame ( buf , columns = [ 'time' , 'open' , 'close' , 'high' , 'low' , 'volume' , 'n1' , 'n2' ] )
	df = df [ [ 'time' , 'open' , 'close' , 'high' , 'low' , 'volume' ] ]
	df [ [ 'open' , 'close' , 'high' , 'low' , 'volume' ] ] = df [
		[ 'open' , 'close' , 'high' , 'low' , 'volume' ] ].astype ( 'float' )
	df.time = pd.to_datetime ( df.time )
	df.set_index ( [ 'time' ] , inplace = True )
	df.index.name = ''
	df [ 'close' ] [ -1 ] = float ( st [ 'data' ] [ code ] [ 'qt' ] [ code ] [ 3 ] )
	return df


def get_price_sina ( code: str , end_date: str = '' , count: int = 10 , frequency: str = '60m' ) -> pd.DataFrame:
	frequency = frequency.replace ( '1d' , '240m' ).replace ( '1w' , '1200m' ).replace ( '1M' , '7200m' ) ;
	mcount = count
	ts = int ( frequency [ :-1 ] ) if frequency [ :-1 ].isdigit () else 1
	if (end_date != '') & (frequency in [ '240m' , '1200m' , '7200m' ]):
		end_date = pd.to_datetime ( end_date ) if not isinstance ( end_date , datetime.date ) else end_date  # 转换成datetime
		unit = 4 if frequency == '1200m' else 29 if frequency == '7200m' else 1  # 4,29多几个数据不影响速度
		count = count + (datetime.datetime.now () - end_date).days // unit  # 结束时间到今天有多少天自然日(肯定 >交易日)
	# print(code,end_date,count)
	URL = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={code}&scale={ts}&ma=5&datalen={count}'
	dstr = json.loads ( requests.get ( URL ).content )
	# df=pd.DataFrame(dstr,columns=['day','open','high','low','close','volume'],dtype='float')
	df = pd.DataFrame ( dstr , columns = [ 'time' , 'open' , 'high' , 'low' , 'close' , 'volume' ] )
	df [ 'open' ] = df [ 'open' ].astype ( float )
	df [ 'high' ] = df [ 'high' ].astype ( float )
	df [ 'low' ] = df [ 'low' ].astype ( float )
	df [ 'close' ] = df [ 'close' ].astype ( float )
	df [ 'volume' ] = df [ 'volume' ].astype ( float )
	df.time = pd.to_datetime ( df.time )
	df.set_index ( [ 'time' ] , inplace = True )
	df.index.name = ''  # 处理索引
	if (end_date != '') & (frequency in [ '240m' , '1200m' , '7200m' ]): return df [ df.index <= end_date ] [ -mcount: ]
	return df


def get_price ( code: str , end_date: str = '' , count: int = 10 , frequency: str = '1d' , fields: Iterable = [ ] ) -> pd.DataFrame:
	xcode = code.replace ( '.XSHG' , '' ).replace ( '.XSHE' , '' )
	xcode = 'sh' + xcode if ('XSHG' in code) else 'sz' + xcode if ('XSHE' in code) else code

	if frequency in [ '1d' , '1w' , '1M' ]:
		try:
			return get_price_day_tx ( xcode , end_date = end_date , count = count , frequency = frequency )
		except:
			return get_price_sina ( xcode , end_date = end_date , count = count , frequency = frequency )

	if frequency in [ '1m' , '5m' , '15m' , '30m' , '60m' ]:
		if frequency in '1m': return get_price_min_tx ( xcode , end_date = end_date , count = count , frequency = frequency )
		try:
			return get_price_min_tx ( xcode , end_date = end_date , count = count , frequency = frequency )
		except:
			return get_price_sina ( xcode , end_date = end_date , count = count , frequency = frequency )


def getCSVDumpFileName ( preceding_days: int = 30 ) -> str:
	date = datetime.date.today ()
	return str ( date ) + '-' + str ( preceding_days ) + 'D-Hist-Ashares.csv'


def all_rows_in_last_X_business_days ( df: pd.DataFrame , preceding_days: int = 30 ) -> bool:
	"""
	Check whether all rows in a DataFrame fall within the most recent 30 business days.
	Args:
		df (pd.DataFrame): DataFrame to check.
		preceding_days: previous days to check
	Returns:
		bool: True if all rows fall within the most recent 30 business days, False otherwise.
	"""
	# Define the start and end dates of the desired data range.
	end_date = datetime.datetime.now ()
	start_date = end_date - datetime.timedelta ( days = preceding_days )

	# Create a mask to filter the DataFrame based on the date range.
	mask = (df [ 'date' ] >= start_date) & (df [ 'date' ] <= end_date) & (df [ 'date' ].dt.dayofweek < 5)

	# Check whether all rows satisfy the mask.
	return mask.all ()


def all_volume_falls_within_peace_range ( df: pd.DataFrame , average: float , peace_level: float = 0.05 ) -> bool:
	"""
	Check whether all rows in a DataFrame have volume within peace volume range ( volume_avg * 1.05, volume_avg * .95, )
	Args:
		df (pd.DataFrame): DataFrame to check.
		peace_level: peaceful level to check
	Returns:
		bool: True if all rows have volume within peace volume range ( volume_avg * 1.05, volume_avg * .95, )
	"""

	# Create a mask to filter the DataFrame based on the date range.
	mask = (df [ 'volume' ] >= average * (1 - peace_level)) & (df [ 'volume' ] <= average * (1 + peace_level))

	# Check whether all rows satisfy the mask.
	return mask.all ()


def getCurrentBJTime () -> datetime.datetime:
	SHA_TZ = datetime.timezone (
		datetime.timedelta ( hours = 8 ) ,
		name = 'Asia/Shanghai' ,
		)
	utc_now = datetime.datetime.utcnow ().replace ( tzinfo = datetime.timezone.utc )
	beijing_now = utc_now.astimezone ( SHA_TZ )
	print ( beijing_now , beijing_now.tzname () )
	return beijing_now


def pick_stocks ( df: pd.DataFrame , volumeSpikeMultiplier: int = 10 , peaceRange: float = 0.05 , preceding_days: int = 30 ) -> List:
	"""
	Identify stocks that meet the following criteria:
		1. Today's trading volume is 10 times the previous 29 days' trading volume average.
		2. For the previous 29 days, each and every day's volume falls in +-5% of the 29-day's volume's average.

	Args:
		df (pd.DataFrame): DataFrame containing open, high, low, volume data for 100 stocks for the past 30 days.

	Returns:
		pd.Series: Series containing the tickers of the stocks that meet the criteria.
	"""
	# Calculate the 29-day moving average of each stock's trading volume.
	df [ 'volume_mean' ] = df.groupby ( 'code' ) [ 'volume' ].mean ()  # .transform ( lambda x: x.rolling ( window = preceding_days ).mean () )

	# Calculate today's trading volume for each stock.
	df [ 'today_volume' ] = df.groupby ( 'code' ) [ 'volume' ].transform ( lambda x: x.iloc [ -1 ] )

	# Filter the DataFrame to include only the most recent day's data.
	today_df = df [ df [ 'date' ] == df [ 'date' ].max () ]

	# Identify stocks that meet the criteria.
	criteria1 = today_df [ 'today_volume' ] > 10 * today_df [ 'volume_mean' ]
	criteria2 = (today_df [ 'today_volume' ] >= today_df [ 'volume_mean' ] * 0.95) & (
			today_df [ 'today_volume' ] <= today_df [ 'volume_mean' ] * 1.05)
	criteria2 = criteria2.groupby ( today_df [ 'ticker' ] ).all ()
	criteria = criteria1 & criteria2
	selected_tickers = today_df.loc [ criteria , 'ticker' ].tolist ()

	return selected_tickers


def get_a_share_hist_data ( preceding_days: int = 30 , peace_level: float = 0.05 ) -> [ pd.DataFrame , pd.DataFrame ]:
	"""
	Get the historical daily trading data for all A share stocks.
	SHOULD Exclude current trading day e.g. running SOD before market open

	Parameters:
	start_date (str): The start date of the data to retrieve (in the format 'YYYY-MM-DD').
					  If not specified, defaults to the earliest available date.
	end_date (str): The end date of the data to retrieve (in the format 'YYYY-MM-DD').
					If not specified, defaults to the latest available date.

	Returns:
	pandas.DataFrame: A DataFrame containing the daily trading data for all A share stocks.
	"""

	dt = getCurrentBJTime ()
	if dt.date ().weekday () <= 5:
		print ( "Checking current time, and it will be too late to start on weekdays' morning after 8 AM" )
	# assert dt.hour <= 8
	time_sec = time.time ()

	# Get the list of A share symbols
	stock_pool: Mapping [ str , Mapping ] = get_stock_pool_today ()
	symbols: List = stock_pool.keys ()
	pbar = ProgressBar ().start ()

	# Get the daily trading data for each A share stock
	dfs = [ ]
	analytics = { }
	invalid_tickers = [ ]
	for i , symbol in enumerate ( symbols ):
		pbar.update ( int ( i / len ( symbols ) * 100 ) )
		df = get_price ( symbol , frequency = '1d' , count = preceding_days + 1 )
		df [ 'code' ] = symbol
		df [ 'date' ] = df.index
		if df is not None and all_rows_in_last_X_business_days ( df , preceding_days + 25 ):

			df.volume = df.volume.astype ( 'float' )
			volume_avg = df.volume.mean ()
			peace = all_volume_falls_within_peace_range ( df , volume_avg , peace_level )
			analytics [ symbol ] = { 'volume_avg': volume_avg , 'peace': peace }
			dfs.append ( df )
		else:
			invalid_tickers.append ( symbol )

	print ( "\n Time in minutes since the epoch:" , (time.time () - time_sec) / 60 )
	print ( "Today's invalid tickers are: " , invalid_tickers )
	# Combine the data for all A share stocks into a single DataFrame
	if dfs:
		a_share_data = pd.concat ( dfs )
		a_share_data.reset_index ( inplace = True )
		a_share_data = a_share_data [ [ 'date' , 'code' , 'open' , 'high' , 'low' , 'close' , 'volume' ] ]
		a_share_data.to_csv ( getCSVDumpFileName ( preceding_days ) )
		analytics_df = pd.DataFrame ( analytics )
		analytics_df.to_csv ( "Analytics-" + getCSVDumpFileName ( preceding_days ) )
		return [ a_share_data , analytics_df ]
	return [ ]


def constructVolumeAnalyticsDF ( hist_data: pd.DataFrame , peace_level: float = 0.05 ) -> pd.DataFrame:
	"""
	Constructs a dataframe with columns ['code', 'avg_volume', 'peace'].
	Each row contains a unique stock code, avg_volume is the average volume for that stock,
	peace is whether each and every day's trading volume falls within (avg_volume * 0.95, avg_volume * 1.05)

	Parameters:
	df (pandas.DataFrame): a dataframe with column: ['date', 'code', 'open', 'high', 'low', 'close', 'volume'].
	Rows are the stock prices for stock code X on date D.

	Returns:
	pandas.DataFrame: a dataframe with columns ['code', 'avg_volume', 'peace'].
	"""
	avg_volume_df = hist_data.groupby ( 'code' ) [ 'volume' ].mean ().reset_index ()
	avg_volume_df.columns = [ 'code' , 'avg_volume' ]

	volume_range_df = hist_data.groupby ( 'code' ) [ 'volume' ].apply ( lambda x: (
			(x > x.mean () * (1 - peace_level)) & (x < x.mean () * (1 + peace_level))).all () ).reset_index ()
	volume_range_df.columns = [ 'code' , 'peace' ]

	result_df = pd.merge ( avg_volume_df , volume_range_df , on = 'code' )

	return result_df


def getPeacefulStocks ( df: pd.DataFrame ) -> List:
	"""
	Constructs a list of stock codes with 'peace' column value as True in the input dataframe.

	Parameters:
	df (pandas.DataFrame): a dataframe with columns ['code', 'avg_volume', 'peace'].

	Returns:
	list: a list of stock codes with 'peace' column value as True.
	"""
	return df.loc [ df [ 'peace' ] , 'code' ].tolist ()


def filter_top_stocks_by_volume_spike ( preceding_days: int = 30 , multiplier_level: int = 10 , peace_level: float = 0.05 ) -> List [ str ]:
	"""
	Filter the top stocks whose trading volume suddenly spikes compared with the preceding trading volume.

	Args:
		stock_pool (dict): A dictionary containing the A-share stock pool, with keys representing the stock ticker and values representing the stock info.
		preceding_days (int): The number of preceding days to compare trading volumes.
		multiplier_level (int): The multiplier level of the trading volume spike.
		peace_level (float): The maximum percentage change allowed in preceding days' trading volume.

	Returns:
		List[str]: A list of the top stock tickers that meet the trading volume spike criteria.
	"""

	# Get the daily trading volume for all A share stocks
	a_share_data: pd.DataFrame = get_a_share_hist_data ( preceding_days = preceding_days , peace_level = peace_level )
	# a_share_data: pd.DataFrame = pd.read_csv ( getCSVDumpFileName ( preceding_days ) )

	avg_volume_data = a_share_data.pivot ( index = 'date' , columns = 'code' , values = 'volume_avg' )
	peace_stock_data = a_share_data.pivot ( index = 'date' , columns = 'code' , values = 'peace' )
	volume_data = a_share_data.pivot_table ( index = 'date' , columns = 'code' , values = 'volume' , aggfunc = 'mean' )

	# Calculate the trading volume change over the preceding days
	preceding_days_volume = volume_data.tail ( preceding_days + 1 ).mean ()
	preceding_days_volume.name = 'preceding_volume'

	current_day_volume = volume_data.tail ( 1 ).transpose ()
	current_day_volume.columns = [ 'current_volume' ]

	top_stocks = [ ]

	# # Calculate the percentage change in the preceding days' volume
	# percent_change_preceding_days = (volume_today - avg_volume_preceding_days) / avg_volume_preceding_days
	#
	# # Check if the volume spike meets the criteria
	# if percent_change_preceding_days <= max_percent_change and volume_today >= (
	# 		multiplier_level * avg_volume_preceding_days):
	# 	top_stocks.append ( stock_ticker )
	#
	# # Sort the top stocks by their volume change percentage
	# top_stocks.sort ( key = lambda x: (get_price ( x , 1 ).iloc [ -1 ] [ 'volume' ] / get_price ( x , preceding_days ) [
	# 	'volume' ].mean ()) , reverse = True )

	return top_stocks


if __name__ == '__main__':
	# df = get_stock_pool_today( 'timekline' )
	# print ( 'Time K Line from QQ \n', df )

	# df = get_stock_pool_today ( 'daykline' )
	# print ( 'Day K Line from QQ \n' , df )

	# df = get_stock_pool_today ( 'hkquote' )
	# print ( 'HK Quote from QQ \n' , df )
	#
	# df = get_stock_pool_today ( 'tencent' )
	# print ( df )  # dict { 5444 }
	"""
	{'name': '平安银行', 'code': 'sz000001', 'now': 12.82, 'close': 12.9, 'open': 12.85, 'volume': 62151900.0, 'bid_volume': 27364500, 'ask_volume': 34787400.0, 'bid1': 12.81, 'bid1_volume': 170500, 'bid2': 12.8, 'bid2_volume': 322100, 'bid3': 12.79, 'bid3_volume': 397500, 'bid4': 12.78, 'bid4_volume': 832200, 'bid5': 12.77, 'bid5_volume': 598300, 'ask1': 12.82, 'ask1_volume': 67600, 'ask2': 12.83, 'ask2_volume': 353200, 'ask3': 12.84, 'ask3_volume': 298200, 'ask4': 12.85, 'ask4_volume': 399400, 'ask5': 12.86, 'ask5_volume': 449500, '最近逐笔成交': '', 'datetime': datetime.datetime(2023, 3, 24, 16, 14, 3), '涨跌': -0.08, '涨跌(%)': -0.62, 'high': 12.86, 'low': 12.76, '价格/成交量(手)/成交额': '12.82/621519/796319542', '成交量(手)': 62151900, '成交额(万)': 796320000.0, 'turnover': 0.32, 'PE': 5.47, 'unknown': '', 'high_2': 12.86, 'low_2': 12.76, '振幅': 0.78, '流通市值': 2487.79, '总市值': 2487.84, 'PB': 0.68, '涨停价': 14.19, '跌停价': 11.61, '量比': 0.59, '委差': 7527.0, '均价': 12.81, '市盈(动)': 5.47, '市盈(静)': 5.47}
	"""
	# sz000003, sz0000015, sz000047, sz000013, sz000405, sz000412, sz000406, sz000024
	# df = get_price ( 'sz000003' , end_date = '2023-03-01' , frequency = '1d' , count = 30 )
	# df [ 'date' ] = df.index
	# val = all_rows_in_last_X_business_days ( df , 30 )
	# print ( '深市日线行情\n' , df )
	#
	df = get_price ( '000001.XSHG' , frequency = '15m' , count = 10 )
	print ( '上证指数分钟线\n' , df )

	# stocks = filter_top_stocks_by_volume_spike ()
	df = constructVolumeAnalyticsDF ( pd.read_csv ( getCSVDumpFileName ( 30 ) ) , peace_level = .2 )
	arr = getPeacefulStocks ( df )
	print ( "Valid tickers" , df )
