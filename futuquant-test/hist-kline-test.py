#!/usr/bin/env python
# -*- coding: utf-8 -*-

from futuquant import *
import time
# 连接到本地 FutuOpenD 网关
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 历史 K 线数据只有到前一天收市的，没有当天的
# 当天的数据什么时候入库？沪深 15:00 收市后大约 半 小时（FutuHistData每半小时开始一次下载）左右开始下载入库，5-10 分钟，港股 16:00 收市后大约 1 小时左右开始下载入库，10-15分钟
while True:
	print("\n" + time.asctime())
	print(quote_ctx.get_history_kline('HK.06866', start='2018-08-28', ktype=KLType.K_DAY))
	time.sleep(600)
# print(quote_ctx.get_multiple_history_kline(['HK.06866', 'HK.02312', 'HK.00491'], '2018-08-27', '2018-08-29', KLType.K_DAY, AuType.QFQ))
quote_ctx.close()