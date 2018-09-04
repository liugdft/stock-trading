#!/usr/bin/env python
# -*- coding: utf-8 -*-

from confluent_kafka import Consumer, KafkaError
from confluent_kafka import TopicPartition
import pandas as pd, json, time
from tabulate import tabulate

# 每只股票都创建 1 个 topic，包含 5 个 partition，partition 0 存放 futu 获取的 snapshot，partition 1 存放 futu 的 实时报价，partition 2 存放 futu 的实时 K线，partition 3 存放 futu 的实时 分时，
# partition 4 存放 futu 的实时 逐比，partition 5 存放 futu 的实时摆盘，partition 6 存放 futu 的实时经纪队列，partition 7-9 暂时空闲
consumer = Consumer({
	'bootstrap.servers': 'Node1',
	'group.id': 'stock_notice',
	'enable.auto.commit': False,
	'default.topic.config': {
		'auto.offset.reset': 'largest'
	}
})
def convert_volume_format(volume):
	# 转换 volume 和 金额 的格式，把包含 万、亿、百万、千万 字样的值转换为数值，方便计算和排序
	

def morning_notice():
	#(rise_ratio_list_smallest, rise_ratio_list_largest) = consumer.get_watermark_offsets(TopicPartition('eastmoney', 0))
	(volume_list_smallest, volume_list_largest) = consumer.get_watermark_offsets(TopicPartition('eastmoney', 0))
	try:
		#consumer.assign([TopicPartition('eastmoney', 0, rise_ratio_list_largest-1)])
		#consumer.seek(TopicPartition('eastmoney', 0, rise_ratio_list_largest-1))
		# consumer.seek(TopicPartition('eastmoney', 0, rise_ratio_list_largest-1))
		# latest_rise_ratio = json.loads(consumer.poll(1.0).value())["data"]
		#latest_rise_ratio = pd.read_json(json.loads(consumer.poll(1.0).value())["data"]).sort_index()
		#latest_rise_ratio["涨幅%"] = latest_rise_ratio["涨幅%"].map(lambda x: float(x.replace('----', '0.00')))
		#print(latest_rise_ratio.head(10))
		last_data_point = volume_list_largest-1
		consumer.assign([TopicPartition('eastmoney', 0, last_data_point)])
		consumer.seek(TopicPartition('eastmoney', 0, last_data_point))
		all_data = json.loads(consumer.poll(3.0).value())
		latest_volume = pd.read_json(all_data["data"]).sort_index()
		latest_volume["涨幅%"] = latest_volume["涨幅%"].map(lambda x: float(x.replace('----', '0.00')))
		latest_volume["金额"] = latest_volume["金额"].map(lambda x: x if else if ))
		result = latest_volume.head(500).sort_values("金额", ascending = False).head(100)
		print("| 当前时间: " + time.strftime("%Y-%m-%d %H:%M:%S") + " | " + "数据更新时间: " + time.strftime("%Y-%m-%d %H:%M:%S" ,time.localtime(all_data["timestamp"]/1000000000)) + " |")
		print(tabulate(result, headers='keys', tablefmt='psql'))
	finally:
		consumer.close()
	#riae_ratio_list = pd.read_json(json.loads(latest_rise_ratio.value()))["data"].sort_index()
	#volume_list = pd.read_json(json.loads(latest_volume.value()))["data"].sort_index()

if __name__ == '__main__':
	morning_notice()
