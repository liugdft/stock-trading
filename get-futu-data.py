#!/usr/bin/env python
# -*- coding: utf-8 -*-

from confluent_kafka import Producer
from confluent_kafka import Consumer, KafkaError
from confluent_kafka import TopicPartition
import pandas as pd, json, time
import futuquant as ft

consumer = Consumer({
	'bootstrap.servers': 'kafka01',
	'group.id': 'futuquant',
	'enable.auto.commit': False,
	'default.topic.config': {
		'auto.offset.reset': 'largest'
	}
})
producer = Producer({'bootstrap.servers': 'kafka01'})
quote_ctx = ft.OpenQuoteContext(host="127.0.0.1", port=11111)

def get_futu_data():
	# 每只股票都创建 1 个 topic，包含 5 个 partition，partition 0 存放 futu 获取的 snapshot，partition 1 存放 futu 的 实时报价，partition 2 存放 futu 的实时 K线，partition 3 存放 futu 的实时 分时，
	# partition 4 存放 futu 的实时 逐比，partition 5 存放 futu 的实时摆盘，partition 6 存放 futu 的实时经纪队列，partition 7-9 暂时空闲

	(rise_ratio_list_smallest, rise_ratio_list_largest) = consumer.get_watermark_offsets(TopicPartition('eastmoney', 0))
	(volume_list_smallest, volume_list_largest) = consumer.get_watermark_offsets(TopicPartition('eastmoney', 1))

	# 设置 dataframe 数据显示的行、列的最大显示范围，否则中间部分会省略为 ...
	#pd.set_option('display.max_rows',500)
	#pd.set_option('display.max_columns',500)

	#consumer.assign([TopicPartition('eastmoney', 0, rise_ratio_list_largest-1)])
	#consumer.seek(TopicPartition('eastmoney', 0, rise_ratio_list_largest-1))
	# consumer.seek(TopicPartition('eastmoney', 0, rise_ratio_list_largest-1))
	# latest_rise_ratio = json.loads(consumer.poll(1.0).value())["data"]
	#latest_rise_ratio = pd.read_json(json.loads(consumer.poll(1.0).value())["data"]).sort_index()
	#latest_rise_ratio["涨幅%"] = latest_rise_ratio["涨幅%"].map(lambda x: float(x.replace('----', '0.00')))
	#print(latest_rise_ratio.head(10))
	consumer.assign([TopicPartition('eastmoney', 1, volume_list_largest-1)])
	consumer.seek(TopicPartition('eastmoney', 1, volume_list_largest-1))
	latest_volume = pd.read_json(json.loads(consumer.poll(1.0).value())["data"]).sort_index()
	latest_volume["涨幅%"] = latest_volume["涨幅%"].map(lambda x: float(x.replace('----', '0.00')))
	watch_stocks = latest_volume.head(200).sort_values("涨幅%", ascending = False).head(100)
	#print(watch_stocks)

	watch_list = watch_stocks["代码"].tolist()
	#print(watch_list)
	#watch_list = ['HK.01091', 'HK.01592', 'HK.00759', 'HK.06866', 'HK.00547']
	_, stock_snapshot = quote_ctx.get_market_snapshot(watch_list)
	#print(stock_snapshot)

	for index,row in stock_snapshot.iterrows():
		producer.produce(row["code"], row.to_json().encode('UTF-8'), partition=0)
		# print(row.to_json())
	producer.flush()
	#riae_ratio_list = pd.read_json(json.loads(latest_rise_ratio.value()))["data"].sort_index()
	#volume_list = pd.read_json(json.loads(latest_volume.value()))["data"].sort_index()

def in_time_range(ranges):
	now = time.strptime(time.strftime("%H%M%S"),"%H%M%S")
	ranges = ranges.split(",")
	for range in ranges:
		r = range.split("-")
		if time.strptime(r[0],"%H%M%S") <= now <= time.strptime(r[1],"%H%M%S") or time.strptime(r[0],"%H%M%S") >= now >=time.strptime(r[1],"%H%M%S"):
			return True
	return False

if __name__ == '__main__':
	while True:
		if in_time_range("090000-120000,130000-163000"):
			get_futu_data()
			if in_time_range("093000-110000,130000-143000"):
				time.sleep(5)
			else:
				time.sleep(15)
		else:
			time.sleep(60)

	consumer.close()
	quote_ctx.close()