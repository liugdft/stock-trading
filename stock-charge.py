#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math, matplotlib.pyplot as plt

def xueying_hk():
	x = []
	y = []
	for i in range(101):
		volume = i * 1000
		x.append(volume)
		# 手续费包括 雪盈的：平台使用费、交易佣金
		# 交易所的：交易系统使用费、交收费、印花税、交易费、交易正费
		charge = 18 + (0 if volume <= 60000 else (volume-60000) * 0.0003) + \
				0.5 + (2 if volume * 0.00002 <= 2 else (100 if volume * 0.00002 >= 100 else volume * 0.00002)) + \
				math.floor(volume * 0.001)+1 + (0.01 if volume * 0.00005 <= 0.01 else volume * 0.00005) + \
				(0.01 if volume * 0.000027 <= 0.01 else volume * 0.000027)
		y.append(charge)
		# print("volume is: " + str(volume) + " and charge is : " + str(charge))
	plt.plot(x, y)
	plt.show()

if __name__ == '__main__':
	xueying_hk()
