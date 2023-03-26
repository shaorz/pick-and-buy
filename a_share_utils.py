import json , requests , datetime
import pandas as pd
from typing import Iterable
import easyquotation


def get_stock_pool_today ( agent: str = 'tencent', withPrefix : bool = True ) -> pd.DataFrame:
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
	st = json.loads ( requests.get ( URL ).content ) ;
	ms = 'qfq' + unit ;
	stk = st [ 'data' ] [ code ]
	buf = stk [ ms ] if ms in stk else stk [ unit ]
	df = pd.DataFrame ( buf , columns = [ 'time' , 'open' , 'close' , 'high' , 'low' , 'volume' ] , dtype = 'float' )
	df.time = pd.to_datetime ( df.time ) ;
	df.set_index ( [ 'time' ] , inplace = True ) ;
	df.index.name = ''
	return df


def get_price_min_tx ( code: str , end_date: str = None , count: int = 10 , frequency: str = '1d' ) -> pd.DataFrame:
	ts = int ( frequency [ :-1 ] ) if frequency [ :-1 ].isdigit () else 1
	if end_date: end_date = end_date.strftime ( '%Y-%m-%d' ) if isinstance ( end_date , datetime.date ) else \
		end_date.split ( ' ' ) [ 0 ]
	URL = f'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={code},m{ts},,{count}'
	st = json.loads ( requests.get ( URL ).content ) ;
	buf = st [ 'data' ] [ code ] [ 'm' + str ( ts ) ]
	df = pd.DataFrame ( buf , columns = [ 'time' , 'open' , 'close' , 'high' , 'low' , 'volume' , 'n1' , 'n2' ] )
	df = df [ [ 'time' , 'open' , 'close' , 'high' , 'low' , 'volume' ] ]
	df [ [ 'open' , 'close' , 'high' , 'low' , 'volume' ] ] = df [
		[ 'open' , 'close' , 'high' , 'low' , 'volume' ] ].astype ( 'float' )
	df.time = pd.to_datetime ( df.time ) ;
	df.set_index ( [ 'time' ] , inplace = True ) ;
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
	dstr = json.loads ( requests.get ( URL ).content ) ;
	# df=pd.DataFrame(dstr,columns=['day','open','high','low','close','volume'],dtype='float')
	df = pd.DataFrame ( dstr , columns = [ 'day' , 'open' , 'high' , 'low' , 'close' , 'volume' ] )
	df [ 'open' ] = df [ 'open' ].astype ( float ) ;
	df [ 'high' ] = df [ 'high' ].astype ( float ) ;  # 转换数据类型
	df [ 'low' ] = df [ 'low' ].astype ( float ) ;
	df [ 'close' ] = df [ 'close' ].astype ( float ) ;
	df [ 'volume' ] = df [ 'volume' ].astype ( float )
	df.day = pd.to_datetime ( df.day ) ;
	df.set_index ( [ 'day' ] , inplace = True ) ;
	df.index.name = ''  # 处理索引
	if (end_date != '') & (frequency in [ '240m' , '1200m' , '7200m' ]): return df [ df.index <= end_date ] [ -mcount: ]
	return df


def get_price ( code: str , end_date: str = '' , count: int = 10 , frequency: str = '1d' , fields: Iterable = [ ] ) -> pd.DataFrame:
	xcode = code.replace ( '.XSHG' , '' ).replace ( '.XSHE' , '' )
	xcode = 'sh' + xcode if ('XSHG' in code) else 'sz' + xcode if ('XSHE' in code) else code

	if frequency in [ '1d' , '1w' , '1M' ]:
		try:
			return get_price_sina ( xcode , end_date = end_date , count = count , frequency = frequency )
		except:
			return get_price_day_tx ( xcode , end_date = end_date , count = count , frequency = frequency )

	if frequency in [ '1m' , '5m' , '15m' , '30m' , '60m' ]:
		if frequency in '1m': return get_price_min_tx ( xcode , end_date = end_date , count = count , frequency = frequency )
		try:
			return get_price_sina ( xcode , end_date = end_date , count = count , frequency = frequency )
		except:
			return get_price_min_tx ( xcode , end_date = end_date , count = count , frequency = frequency )


if __name__ == '__main__':

	# df = get_stock_pool_today( 'timekline' )
	# print ( 'Time K Line from QQ \n', df )

	# df = get_stock_pool_today ( 'daykline' )
	# print ( 'Day K Line from QQ \n' , df )

	# df = get_stock_pool_today ( 'hkquote' )
	# print ( 'HK Quote from QQ \n' , df )

	df = get_stock_pool_today( 'tencent' )
	print ( df ) # dict { 5444 }
	"""
	{'name': '平安银行', 'code': 'sz000001', 'now': 12.82, 'close': 12.9, 'open': 12.85, 'volume': 62151900.0, 'bid_volume': 27364500, 'ask_volume': 34787400.0, 'bid1': 12.81, 'bid1_volume': 170500, 'bid2': 12.8, 'bid2_volume': 322100, 'bid3': 12.79, 'bid3_volume': 397500, 'bid4': 12.78, 'bid4_volume': 832200, 'bid5': 12.77, 'bid5_volume': 598300, 'ask1': 12.82, 'ask1_volume': 67600, 'ask2': 12.83, 'ask2_volume': 353200, 'ask3': 12.84, 'ask3_volume': 298200, 'ask4': 12.85, 'ask4_volume': 399400, 'ask5': 12.86, 'ask5_volume': 449500, '最近逐笔成交': '', 'datetime': datetime.datetime(2023, 3, 24, 16, 14, 3), '涨跌': -0.08, '涨跌(%)': -0.62, 'high': 12.86, 'low': 12.76, '价格/成交量(手)/成交额': '12.82/621519/796319542', '成交量(手)': 62151900, '成交额(万)': 796320000.0, 'turnover': 0.32, 'PE': 5.47, 'unknown': '', 'high_2': 12.86, 'low_2': 12.76, '振幅': 0.78, '流通市值': 2487.79, '总市值': 2487.84, 'PB': 0.68, '涨停价': 14.19, '跌停价': 11.61, '量比': 0.59, '委差': 7527.0, '均价': 12.81, '市盈(动)': 5.47, '市盈(静)': 5.47}
	"""

	df = get_price ( 'sh000001' , frequency = '1d' , count = 10 )
	print ( '上证指数日线行情\n' , df )

	df = get_price ( '000001.XSHG' , frequency = '15m' , count = 10 )
	print ( '上证指数分钟线\n' , df )
