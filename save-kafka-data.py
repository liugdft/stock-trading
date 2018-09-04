#!/usr/bin/env python
# -*- coding: utf-8 -*-

from confluent_kafka import Consumer, KafkaError
from confluent_kafka import TopicPartition
import pandas as pd, json

consumer = Consumer({
	'bootstrap.servers': 'Node1',
	'group.id': 'data_saver',
	'enable.auto.commit': False,
	'socket.keepalive.enable': True,
	'default.topic.config': {
		'auto.offset.reset': 'smallest'
	}
})

# 2018.09.03 40 支股票只订阅 SubType.TICKER, SubType.ORDER_BOOK 用额度 400
stock_list = [ "HK.00788", "HK.03988", "HK.00939", "HK.00136", "HK.00274", "HK.02799", "HK.01398", "HK.00279", "HK.00857", "HK.01288",
			"HK.06828", "HK.02312", "HK.00493", "HK.02326", "HK.00386", "HK.00707", "HK.03800", "HK.00228", "HK.01359", "HK.00024",
			"HK.01177", "HK.03323", "HK.02628", "HK.00539", "HK.00326", "HK.00883", "HK.06098", "HK.02869", "HK.01060", "HK.00728",
			"HK.00721", "HK.00700", "HK.01468", "HK.03993", "HK.02238", "HK.01066", "HK.00139", "HK.02007", "HK.00554", "HK.06878"]

# stock_list = [ "HK.00788" ]

for stock in stock_list:
	# 存储 ticker 和 order_book 数据到 csv 文件
	# 存储 ticker 和 order_book 数据到 influxdb 数据库
	# ticker 在 partition 4
	# ticker_sample_1 = '{"code":"HK.00386","time":"2018-09-03 15:59:50","price":7.67,"volume":4000,"turnover":30680.0,"ticker_direction":"BUY","sequence":6596904796962160642,"type":"AUTO_MATCH"}'
	# ticker_sample_2 = '{"code":"HK.00386","time":"2018-09-03 15:59:50","price":7.67,"volume":2000,"turnover":15340.0,"ticker_direction":"BUY","sequence":6596904796962160644,"type":"AUTO_MATCH"}'
	# ticker_sample_3 = '{"code":"HK.00386","time":"2018-09-03 15:59:51","price":7.67,"volume":2000,"turnover":15340.0,"ticker_direction":"BUY","sequence":6596904801257127938,"type":"AUTO_MATCH"}'
	consumer.assign([TopicPartition(stock, 4, 0)])
	consumer.seek(TopicPartition(stock, 4, 0))
	ticker_pd = pd.DataFrame(columns=['code', 'time', 'price', 'volume', 'turnover', 'ticker_direction', 'sequence', 'type'])
	while True:
		msg = consumer.poll(3.0)
		if msg is None:
			continue
		if msg.error():
			if msg.error().code() == KafkaError._PARTITION_EOF:
				break
			else:
				print(msg.error())
				break
		# print('Received message: {}'.format(msg.value().decode('utf-8')))
		msg_json = json.loads(msg.value())
		ticker_pd = ticker_pd.append([msg_json], ignore_index=True)
	# print(ticker_pd)
	ticker_pd.to_csv("/home/liugdft/stock/ticker-orderbook-sample/2018.09.03/" + stock + "-ticker-20180903.csv")
	# consumer.commit()

	# order_book 在 partition 5
	# orderbook_sample_1 = '{"code": "HK.00386", "Bid": [[7.66, 118000, 6], [7.65, 1618000, 33], [7.64, 354000, 9], [7.63, 546000, 17], [7.62, 2166000, 19], [7.61, 456000, 10], [7.6, 1136000, 18], [7.59, 1320000, 7], [7.58, 1022000, 5], [7.57, 1058000, 6]], "Ask": [[7.67, 1626000, 51], [7.68, 852000, 8], [7.69, 368000, 10], [7.7, 1142000, 9], [7.71, 560000, 5], [7.72, 188000, 7], [7.73, 608000, 9], [7.74, 106000, 4], [7.75, 168000, 6], [7.76, 24000, 2]], "time": "2018-09-03 15:53:56"}'
	# orderbook_sample_2 = '{"code": "HK.00386", "Bid": [[7.66, 186000, 7], [7.65, 1554000, 32], [7.64, 354000, 9], [7.63, 546000, 17], [7.62, 2166000, 19], [7.61, 456000, 10], [7.6, 1136000, 18], [7.59, 1320000, 7], [7.58, 1022000, 5], [7.57, 1058000, 6]], "Ask": [[7.67, 1626000, 51], [7.68, 852000, 8], [7.69, 368000, 10], [7.7, 1142000, 9], [7.71, 560000, 5], [7.72, 188000, 7], [7.73, 608000, 9], [7.74, 106000, 4], [7.75, 168000, 6], [7.76, 24000, 2]], "time": "2018-09-03 15:53:59"}'
	# orderbook_sample_3 = '{"code": "HK.00386", "Bid": [[7.66, 104000, 5], [7.65, 1622000, 33], [7.64, 354000, 9], [7.63, 546000, 17], [7.62, 2166000, 19], [7.61, 456000, 10], [7.6, 1136000, 18], [7.59, 1320000, 7], [7.58, 1022000, 5], [7.57, 1058000, 6]], "Ask": [[7.67, 1626000, 51], [7.68, 852000, 8], [7.69, 368000, 10], [7.7, 1142000, 9], [7.71, 560000, 5], [7.72, 188000, 7], [7.73, 608000, 9], [7.74, 106000, 4], [7.75, 168000, 6], [7.76, 24000, 2]], "time": "2018-09-03 15:53:59"}'
	consumer.assign([TopicPartition(stock, 5, 0)])
	consumer.seek(TopicPartition(stock, 5, 0))
	orderbook_pd = pd.DataFrame(columns=['code', 'Bid', 'Ask', 'time'])
	while True:
		msg = consumer.poll(3.0)
		if msg is None:
			continue
		if msg.error():
			if msg.error().code() == KafkaError._PARTITION_EOF:
				break
			else:
				print(msg.error())
				break
		# print('Received message: {}'.format(msg.value().decode('utf-8')))
		msg_json = json.loads(msg.value())
		orderbook_pd = orderbook_pd.append([msg_json], ignore_index=True)
	# print(orderbook_pd)
	orderbook_pd.to_csv("/home/liugdft/stock/ticker-orderbook-sample/2018.09.03/" + stock + "-orderbook-20180903.csv")
	# consumer.commit()

consumer.close()