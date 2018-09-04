#!/usr/bin/env python
# -*- coding: utf-8 -*-

import futuquant as ft
import pandas as pd, json, time
from influxdb import InfluxDBClient

quote_ctx = ft.OpenQuoteContext(host="127.0.0.1", port=11111)
client = InfluxDBClient('10.2.1.10', 8086)

def get_stock_list():
	# 由于 get_plate_stock 的频率限制为 30 秒钟 10 次，所以每次获取要 sleep(3)
	# 全部港股(正股)
	_, HK_all_stocks = quote_ctx.get_plate_stock("HK.999999")
	time.sleep(3)
	# 港股主板
	_, HK_main_stocks = quote_ctx.get_plate_stock("HK.999910")
	time.sleep(3)
	# 港股创业板
	_, HK_GEM_stocks = quote_ctx.get_plate_stock("HK.999911")
	time.sleep(3)
	# 沪深全部A股
	_, CN_all_stocks = quote_ctx.get_plate_stock("SH.3000005")
	time.sleep(3)
	# 上海主板
	_, SH_main_stocks = quote_ctx.get_plate_stock("SH.3000000")
	time.sleep(3)
	# 深圳主板
	_, SZ_main_stocks = quote_ctx.get_plate_stock("SZ.3000001")
	time.sleep(3)
	# 中小企业板块
	_, SZ_SME_stocks = quote_ctx.get_plate_stock("SZ.3000003")
	time.sleep(3)
	# 深证创业板
	_, SZ_GEM_stocks = quote_ctx.get_plate_stock("SZ.3000004")
	time.sleep(3)
	# 全部美股(正股)
	_, US_all_stocks = quote_ctx.get_plate_stock("US.200306")
	time.sleep(3)
	# 纽交所
	_, US_NYSE_stocks = quote_ctx.get_plate_stock("US.200301")
	time.sleep(3)
	# 纳斯达克
	_, US_NASDAQ_stocks = quote_ctx.get_plate_stock("US.200302")
	time.sleep(3)
	# 美交所
	_, US_AMEX_stocks = quote_ctx.get_plate_stock("US.200303")
	time.sleep(3)

	print("全部港股(正股) 总数量： " + str(HK_all_stocks.count()[0]))
	print("港股主板 总数量： " + str(HK_main_stocks.count()[0]))
	print("港股创业板 总数量： " + str(HK_GEM_stocks.count()[0]))
	print("沪深全部A股 总数量： " + str(CN_all_stocks.count()[0]))
	print("上海主板 总数量： " + str(SH_main_stocks.count()[0]))
	print("深圳主板 总数量： " + str(SZ_main_stocks.count()[0]))
	print("中小企业板块 总数量： " + str(SZ_SME_stocks.count()[0]))
	print("深证创业板 总数量： " + str(SZ_GEM_stocks.count()[0]))
	print("全部美股(正股) 总数量： " + str(US_all_stocks.count()[0]))
	print("纽交所 总数量： " + str(US_NYSE_stocks.count()[0]))
	print("纳斯达克 总数量： " + str(US_NASDAQ_stocks.count()[0]))
	print("美交所 总数量： " + str(US_AMEX_stocks.count()[0]))

	# 将获取的数据存入数据库
	db = "stock-info"
	stock_list = [
		{
			"measurement": "plate-stocks",
			"time": time.time_ns(),
			"fields": {
				"HK_all_stocks" : HK_all_stocks.to_json(),
				"HK_main_stocks" : HK_main_stocks.to_json(),
				"HK_GEM_stocks" : HK_GEM_stocks.to_json(),
				"CN_all_stocks" : CN_all_stocks.to_json(),
				"SH_main_stocks" : SH_main_stocks.to_json(),
				"SZ_main_stocks" : SZ_main_stocks.to_json(),
				"SZ_SME_stocks" : SZ_SME_stocks.to_json(),
				"SZ_GEM_stocks" : SZ_GEM_stocks.to_json(),
				"US_all_stocks" : US_all_stocks.to_json(),
				"US_NYSE_stocks" : US_NYSE_stocks.to_json(),
				"US_NASDAQ_stocks" : US_NASDAQ_stocks.to_json(),
				"US_AMEX_stocks" : US_AMEX_stocks.to_json()
			}
		}
	]

	print(stock_list)
	client.write_points(stock_list, database=db)
	# result = client.query('select * from "plate-stocks"', database=db)
	# print("Result: {0}".format(result))

if __name__ == '__main__':
	get_stock_list()
	quote_ctx.close()
	client.close()