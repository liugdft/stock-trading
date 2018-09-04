#!/usr/bin/env python
# -*- coding: utf-8 -*-

from futuquant import *
import pandas as pd
# 连接到本地 FutuOpenD 网关
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 设置 dataframe 数据显示的行、列的最大显示范围，否则中间部分会省略为 ...
pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',500)

# 获取交易日，默认获取近一年的
_, trade_date = quote_ctx.get_trading_days(Market.HK, start_date=None, end_date=None)

# 获取股票信息
_, stock_info = quote_ctx.get_stock_basicinfo(Market.HK, stock_type=SecurityType.STOCK)

# 获取港股主板的股票列表，HK.999911 是创业板，HK.999999 是全部港股（正股）
_, main_stocks = quote_ctx.get_plate_stock('HK.999910')

watch_stocks = ['HK.00632', 'HK.00456']
# 获取市场快照，一次最多 200 个票, 每 30 秒内只能获取 10 次
# Q：市场快照的实时性？ - 获取的是均线价格，如果价格没有变动，updte_time 和数据就不会变
_, market_snapshot = quote_ctx.get_market_snapshot(watch_stocks)
market_snapshot['rise_ratio'] = market_snapshot.apply(lambda x: x[code], axis=1)

# 获取历史 K 线数据，从 HistData 里取
quote_ctx.get_history_kline(, start=None, end=None, ktype=KLType.K_DAY, autype=AuType.QFQ)

# 获取复权因子
_, autpye = quote_ctx.get_autype_list(watch_stocks)

# 获取板块下的子板块，然后再获取子板块的股票列表
_, subplate = quote_ctx.get_plate_list(Market.HK, Plate.ALL)
#_, main_stocks = quote_ctx.get_plate_stock(subplate[x][x])

# 获取 K 线数据，一次最多 1000 根
_, kline_1min = get_cur_kline()

# 首先获取所有香港主板股票的当前报价列表，根据涨跌幅排序，然后按照总量/金额排序，然后再按照换手率排序，筛选出关注的股票

# 根据下载的 1分钟、5分钟、15分钟、30分钟 K 线数据，计算出稳赢线、JD、MACD
# 三个指标的数值，经过比较后，列出有机会的票，微信进行提醒


print(quote_ctx.get_rt_data('HK.00700'))
#quote_ctx.get_rt_data('HK.00700')[1].to_csv('HK.00700-snapshot.csv', index=False)




# 程序结束，关闭连接
quote_ctx.close()
