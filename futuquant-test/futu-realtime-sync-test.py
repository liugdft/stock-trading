#!/usr/bin/env python
# -*- coding: utf-8 -*-

import futuquant as ft, time
# 连接到本地 FutuOpenD 网关
quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)

result = quote_ctx.subscribe(["HK.06866", "HK.02312", "HK.01630"], [ft.SubType.TICKER, ft.SubType.QUOTE, ft.SubType.ORDER_BOOK, ft.SubType.K_1M, ft.SubType.K_5M, ft.SubType.K_15M, ft.SubType.RT_DATA, ft.SubType.BROKER])
print("subscribe result: " + time.asctime())
print(result)

result = quote_ctx.query_subscription()
print("query_subscription result: " + time.asctime())
print(result)

result = quote_ctx.get_stock_quote(["HK.06866", "HK.02312", "HK.01630"])
print("get_stock_quote result: " + time.asctime())
print(result)

for stock in ["HK.06866", "HK.02312", "HK.01630"]:
	result = quote_ctx.get_rt_ticker(stock, 1000)
	print("get_rt_ticker result: " + time.asctime())
	print(result)

	result = quote_ctx.get_order_book(stock)
	print("get_order_book result: " + time.asctime())
	print(result)

	result = quote_ctx.get_cur_kline(stock, 100, ft.SubType.K_1M)
	print("get_cur_kline 1m result: " + time.asctime())
	print(result)

	result = quote_ctx.get_cur_kline(stock, 100, ft.SubType.K_5M)
	print("get_stockget_cur_kline 5m result: " + time.asctime())
	print(result)

	result = quote_ctx.get_cur_kline(stock, 100, ft.SubType.K_15M)
	print("get_cur_kline 15m result: " + time.asctime())
	print(result)

	result = quote_ctx.get_rt_data(stock)
	print("get_rt_data result: " + time.asctime())
	print(result)

	result = quote_ctx.get_broker_queue(stock)
	print("get_broker_queue result: " + time.asctime())
	print(result)

# subscribe 之后至少要 1 分钟才能 unsubscribe，即使对于没有 subscribe 的股票，unsubscribe 也会返回正常值，不会报错
# 哪个连接订阅的票，只能由自己 unsubscribe，其他连接在 query_subscription 能够看到总的，但是不能 unsubscribe 不是自己连接下 subscribe 的票
# 两个连接同时 subscribe 一个票呢？以第一个订阅的连接为主
# 另一个连接已经 close() 了呢？close() 以后，连接 subscribe 的票自动 unsubscribe，如果没有到 1 分钟就 close() 了，则订阅会保留，直到超时后自动 unsubscribe
# 不同的连接 subscribe 的票，能不能互相获取数据？不能，query_subscription 获取的是总的额度信息，但是每个连接只能获取自己 subscribe 的票的内容

time.sleep(60)

result = quote_ctx.unsubscribe(["HK.06866", "HK.02312", "HK.01630"], [ft.SubType.TICKER, ft.SubType.QUOTE, ft.SubType.ORDER_BOOK, ft.SubType.K_1M, ft.SubType.K_5M, ft.SubType.K_15M, ft.SubType.RT_DATA, ft.SubType.BROKER])
print("unsubscribe result: " + time.asctime())
print(result)

result = quote_ctx.query_subscription()
print("query_unsubscription result: " + time.asctime())
print(result)

quote_ctx.close()