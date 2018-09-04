#!/usr/bin/env python
# -*- coding: utf-8 -*-

from confluent_kafka import Consumer, KafkaError
from confluent_kafka import TopicPartition
from influxdb import DataFrameClient, InfluxDBClient
import pandas as pd, json, time, schedule, atexit
import futuquant as ft

# 该文件用于盘中、盘后下载当天的历史实时数据，如 K 线、分时 数据量不大。全部股票或者指定排名前多少的股票
# 下载这些全部的历史数据干什么？FutuHistData 都已经下载了，只有 分时 数据有盘后下载的必要

consumer = Consumer({
	'bootstrap.servers': 'Node1',
	'group.id': 'ticker_downloader',
	'enable.auto.commit': False,
	'socket.keepalive.enable': True,
	'default.topic.config': {
		'auto.offset.reset': 'largest'
	}
})

quote_ctx = ft.OpenQuoteContext(host="127.0.0.1", port=11111)
dbclient = DataFrameClient('Node1', 8086)
dbquery = InfluxDBClient('Node1', 8086)
all_subtypes = [ ft.SubType.TICKER, ft.SubType.QUOTE, ft.SubType.ORDER_BOOK, ft.SubType.K_1M, ft.SubType.K_5M, ft.SubType.K_15M, ft.SubType.K_30M, ft.SubType.K_60M, ft.SubType.K_DAY, ft.SubType.K_WEEK, ft.SubType.K_MON, ft.SubType.RT_DATA, ft.SubType.BROKER ]
subscribe_subtypes = [ ft.SubType.RT_DATA ]

def clean_atexit():
	try:
		consumer.close()
		quote_ctx.close()

def get_all_data(market, scope):
	if market == "HK":
		if scope == "all":
			# 从数据库获取最近更新的 plate-stocks 数据，或者从 futu 获取也行
			# DataFrameClient query 获取的数据，时间总是有问题，无论怎么都显示为 UTC 时间，换 InfluxDBClient query 就可以
			# dbquery.query("SELECT HK_main_stocks FROM \"plate-stocks\" ORDER BY time DESC LIMIT 1 tz('Asia/Shanghai')", database="stock-info")
			
			# 全部港股(正股)
			_, HK_all_stocks = quote_ctx.get_plate_stock("HK.999999")
			stock_list = HK_all_stocks["code"].tolist()

		elif scope == "top120":
			(volume_list_smallest, volume_list_largest) = consumer.get_watermark_offsets(TopicPartition('eastmoney', 0))
			last_data_point = volume_list_largest-1
			consumer.assign([TopicPartition('eastmoney', 0, last_data_point)])
			consumer.seek(TopicPartition('eastmoney', 0, last_data_point))
			all_data = json.loads(consumer.poll(3.0).value())
			latest_volume = pd.read_json(all_data["data"]).sort_index()
			top120_list = latest_volume.head(120)
			stock_list = top120_list["代码"].tolist()
		else:
			return "None defined donwload scope"
	# elif market == "US":
	# elif market == "CN":
	else:
		return "None defined market"

	# print(stock_list)
	step = 15
	for i in range(0, len(stock_list), step):
		sub_stock_list = stock_list[i : i + step]
		result = quote_ctx.subscribe(sub_stock_list, subscribe_subtypes)
		print("subscribe result: " + time.asctime())
		print(result)
		
		for stock in sub_stock_list:
			ret_code, ret_data = quote_ctx.get_rt_ticker(stock, num=1000)
			if ret_code == 0:
				#print(ret_data)
				# write_points 传入的 dataframe 时间戳必须是转换成标准的格式，并且必须是按照时间排序的
				ret_data["time"] = pd.to_datetime(ret_data["time"])
				ret_data = ret_data.set_index("time")
				# 存入 influxdb 之前，先将时间戳转换为 本地时间，write_points 在存的时候会以 UTC 时间存储
				ret_data.index = ret_data.index.tz_localize('Asia/Shanghai')
				#print(ret_data)
				dbclient.write_points(ret_data, "futu_rt_ticker", tag_columns=['sequence'], database="test")

		time.sleep(60)
		result = quote_ctx.unsubscribe(sub_stock_list, subscribe_subtypes)
		print("unsubscribe result: " + time.asctime())
		print(result)
		# unsubscirbe 后要等一会再订阅，FutuOpenD 在数据量积累到很大的时候会有点慢
		time.sleep(2)

	return True

if __name__ == '__main__':
	#atexit.register(clean_atexit)
	get_all_data("HK")
	# get_ticker_data("HK", "all")
	consumer.close()
	quote_ctx.close()
	dbclient.close()
	dbquery.close()