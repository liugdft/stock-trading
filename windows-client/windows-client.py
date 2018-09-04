#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, logging, json, time, atexit

# 初始化日志信息
log_file = '/home/liugdft/stock/stock-trading/windows-client/windows-client.log'
logger = logging.getLogger("windows-client")
logger.setLevel(logging.DEBUG)

# 日志打印到文件，同时也输出到前端
log_handler = logging.FileHandler(log_file)
log_handler.setLevel(logging.DEBUG)
cmd_handler = logging.StreamHandler()
cmd_handler.setLevel(logging.DEBUG)
log_format = logging.Formatter("[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s")
log_handler.setFormatter(log_format)
cmd_handler.setFormatter(log_format)
logger.addHandler(log_handler)
logger.addHandler(cmd_handler)

host = ('10.2.11.35', 10000)

def clean_atexit():
	client_socket.close()

def command_client(sort_by_value):
	client_socket = socket.socket()
	try:
		client_socket.connect(host)
	except:
		logger.error('connection failed, try again')
		time.sleep(3)
		client_socket.connect(host)
	# message = input(" -> ")
	command = {"command":"get_stocksort", "parameter":{"stock_plate":"hk_main_plate", "sort_by":sort_by_value}}
	# command = {"command":"get_stocksort", "parameter":{"stock_plate":"hk_main_plate", "sort_by":"rise_ratio/volume"}}
	command_stream = json.dumps(command)

	# while message.lower().strip() != 'bye':
	client_socket.sendall(command_stream.encode("UTF-8"))
	try:
		feedback_message = client_socket.recv(1024).decode("UTF-8")
	except:
		logger.error('receive server feedback failed')
		client_socket.close()
		return False
	else:
		logger.info('received feedback from server: ' + feedback_message)
		client_socket.close()

def in_time_range(ranges):
	now = time.strptime(time.strftime("%H%M%S"),"%H%M%S")
	ranges = ranges.split(",")
	for range in ranges:
		r = range.split("-")
		if time.strptime(r[0],"%H%M%S") <= now <= time.strptime(r[1],"%H%M%S") or time.strptime(r[0],"%H%M%S") >= now >=time.strptime(r[1],"%H%M%S"):
			return True
	return False


if __name__ == '__main__':
	atexit.register(clean_atexit)
	while True:
		# command_client("volume")
		if in_time_range("093000-120000,130000-160000"):
			# command_client("rise_ratio")
			command_client("volume")
			if in_time_range("093000-110000,130000-143000"):
				time.sleep(5)
			else:
				time.sleep(5)
		else:
			time.sleep(1)
