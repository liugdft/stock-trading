#!/usr/bin/env python
# -*- coding: utf-8 -*-

from confluent_kafka import Producer
from futuquant import *
import time, pandas as pd, json, os
# 连接到本地 FutuOpenD 网关
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
#f = open("/home/liugdft/stock/stock-trading/futuquant-test/async-data.txt","a")
producer = Producer({'bootstrap.servers': 'Node1',
					# 设置最大缓存大小和提高缓存消息数量，以解决运行过程中 Queue full 的问题，缓存大小最多 2097151KB，约2GB
					'queue.buffering.max.kbytes': 1024000,
					# 不等待，立即发送
					'queue.buffering.max.ms': 0,
					'socket.keepalive.enable': True,
					'queue.buffering.max.messages': 1000000
					})
# 40 支股票只订阅 SubType.TICKER, SubType.ORDER_BOOK 用额度 400
stock_list = [ "HK.00788", "HK.03988", "HK.00939", "HK.00136", "HK.00274", "HK.02799", "HK.01398", "HK.00279", "HK.00857", "HK.01288",
			"HK.06828", "HK.02312", "HK.00493", "HK.02326", "HK.00386", "HK.00707", "HK.03800", "HK.00228", "HK.01359", "HK.00024",
			"HK.01177", "HK.03323", "HK.02628", "HK.00539", "HK.00326", "HK.00883", "HK.06098", "HK.02869", "HK.01060", "HK.00728",
			"HK.00721", "HK.00700", "HK.01468", "HK.03993", "HK.02238", "HK.01066", "HK.00139", "HK.02007", "HK.00554", "HK.06878"]
all_subtypes = [ SubType.TICKER, SubType.QUOTE, SubType.ORDER_BOOK, SubType.K_1M, SubType.K_5M, SubType.K_15M, SubType.K_30M, SubType.K_60M, SubType.K_DAY, SubType.K_WEEK, SubType.K_MON, SubType.RT_DATA, SubType.BROKER ]
subscribe_subtypes = [ SubType.TICKER, SubType.ORDER_BOOK ]

class OrderBookTest(OrderBookHandlerBase):
		def on_recv_rsp(self, rsp_str):
				timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
				# timestamp = time.time_ns()
				# 返回的 data 是一个字典
				ret_code, data = super(OrderBookTest,self).on_recv_rsp(rsp_str)
				data["time"] = timestamp
				if ret_code != RET_OK:
						# f.write("got error!")
						# f.flush()
						# f.close()
						print("OrderBookTest: error, msg: %s" % data)
						return RET_ERROR, data
				data_stream = json.dumps(data)
				try:
					producer.produce(data["code"], data_stream.encode('UTF-8'), partition=5)
					producer.poll(0)
				except:
					print("send a OderBook message failed, try again")
					producer.poll(1)
				#f.write("async get_order_book result: \n" + data_stream + "\n")
				#f.flush()
				# f.close()
				# print("async get_order_book result: " + time.asctime(), data) # OrderBookTest自己的处理逻辑
				return RET_OK, data

class TickerTest(TickerHandlerBase):
		def on_recv_rsp(self, rsp_str):
				# ticker 数据自带时间戳，而且和本地的时间戳结果是一样的
				# timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
				# timestamp = time.time_ns()
				# 返回的 data 是一个Dataframe,会有一次返回多条数据的情况吗？是的
				ret_code, data = super(TickerTest,self).on_recv_rsp(rsp_str)
				if ret_code != RET_OK:
						# f.write("got error!")
						# f.flush()
						# f.close()
						print("TickerTest: error, msg: %s" % data)
						return RET_ERROR, data
				# data["localtime"] = timestamp
				for index, row in data.iterrows():
					data_stream = row.to_json()
					try:
						producer.produce(row["code"], data_stream.encode('UTF-8'), partition=4)
						producer.poll(0)
					except:
						print("send a Tick message failed, try again")
						producer.poll(1)
					#f.write("async get_ticker result: \n" + data_stream + "\n")
					#f.flush()
				# f.close()
				# print("async get_order_book result: " + time.asctime(), data) # TickerTest
				return RET_OK, data

result = quote_ctx.subscribe(stock_list, subscribe_subtypes)
print("subscribe result: " + time.asctime())
print(result)

result = quote_ctx.query_subscription()
print("query_subscription result: " + time.asctime())
print(result)

orderbook_handler = OrderBookTest()
ticker_handler = TickerTest()
quote_ctx.set_handler(orderbook_handler)
quote_ctx.set_handler(ticker_handler)

def in_time_range(ranges):
	now = time.strptime(time.strftime("%H%M%S"),"%H%M%S")
	ranges = ranges.split(",")
	for range in ranges:
		r = range.split("-")
		if time.strptime(r[0],"%H%M%S") <= now <= time.strptime(r[1],"%H%M%S") or time.strptime(r[0],"%H%M%S") >= now >=time.strptime(r[1],"%H%M%S"):
			return True
	return False

# set_handler 之后,已经自动开始了,start() 可要可不要,标准动作而已
quote_ctx.start()
# subscribe 之后至少要 1 分钟才能 unsubscribe,即使对于没有 subscribe 的股票,unsubscribe 也会返回正常值,不会报错
# 哪个连接订阅的票,只能由自己 unsubscribe,其他连接在 query_subscription 能够看到总的,但是不能 unsubscribe 不是自己连接下 subscribe 的票
# 两个连接同时 subscribe 一个票呢？以第一个订阅的连接为主
# 另一个连接已经 close() 了呢？close() 以后,连接 subscribe 的票自动 unsubscribe,如果没有到 1 分钟就 close() 了,则订阅会保留,直到超时后自动 unsubscribe
# 不同的连接 subscribe 的票,能不能互相获取数据？不能,query_subscription 获取的是总的额度信息,但是每个连接只能获取自己 subscribe 的票的内容

# 异步订阅,除遵循以上订阅的规则外,主进程不能退出,接收消息的子线程才能继续工作,quote_ctx.stop()、quote_ctx.unsubscribe、quote_ctx.close(),都能使接收停止
# 异步订阅适合实时接收数据,实时处理没有重复的,同步订阅适合下载历史数据,会有很多重复,例如每次下载最近的 100 条k线或者最近 100 条逐笔记录,就会有很多重复的
# quote_ctx.set_handler 只能指定一个,怎么同时指定接收多个呢？
# quote_ctx.set_handler(StockQuoteTest())
# quote_ctx.set_handler(CurKlineTest())
# quote_ctx.set_handler(RTDataTest())
# quote_ctx.set_handler(TickerTest())
# quote_ctx.set_handler(OrderBookTest())
# quote_ctx.set_handler(BrokerTest())
# quote_ctx.set_handler(SysNotifyTest())
# quote_ctx.start()

while True:
	cmd = input("输入命令: ")
	if cmd == "exit":
		quote_ctx.stop()

		result = quote_ctx.unsubscribe(stock_list, subscribe_subtypes)
		print("unsubscribe result: " + time.asctime())
		print(result)

		result = quote_ctx.query_subscription()
		print("query_unsubscription result: " + time.asctime())
		print(result)

		# f.flush()
		# f.close()
		producer.flush()
		quote_ctx.close()
		break