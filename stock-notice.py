#!/usr/bin/env python
# -*- coding: utf-8 -*-

from confluent_kafka import Consumer, KafkaError
from confluent_kafka import TopicPartition
import pandas as pd, json

def morning_notice():
	# 每只股票都创建 1 个 topic，包含 5 个 partition，partition 0 存放 futu 获取的 snapshot，partition 1 存放 futu 的 实时报价，partition 2 存放 futu 的实时 K线，partition 3 存放 futu 的实时 分时，
	# partition 4 存放 futu 的实时 逐比，partition 5 存放 futu 的实时摆盘，partition 6 存放 futu 的实时经纪队列，partition 7-9 暂时空闲
	consumer = Consumer({
		'bootstrap.servers': 'kafka01',
		'group.id': 'stock_notice',
		'enable.auto.commit': False,
		'default.topic.config': {
			'auto.offset.reset': 'largest'
		}
	})

	(rise_ratio_list_smallest, rise_ratio_list_largest) = consumer.get_watermark_offsets(TopicPartition('eastmoney', 0))
	(volume_list_smallest, volume_list_largest) = consumer.get_watermark_offsets(TopicPartition('eastmoney', 1))
	try:
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
		print(latest_volume.head(100).sort_values("涨幅%", ascending = False).head(10))

	finally:
		consumer.close()
	#riae_ratio_list = pd.read_json(json.loads(latest_rise_ratio.value()))["data"].sort_index()
	#volume_list = pd.read_json(json.loads(latest_volume.value()))["data"].sort_index()

if __name__ == '__main__':
	morning_notice()
