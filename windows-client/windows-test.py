#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import logging
import json

log_file = r'C:\Users\LiuGDFT\Desktop\stock-data\stock-windows.log'
logger = logging.getLogger("windos-client")
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

# 测试日志
# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warn message')
# logger.error('error message')
# logger.critical('critical message')

def windows_server():
	host = '0.0.0.0'
	port = 10000
	server_socket = socket.socket()
	server_socket.bind((host, port))
	server_socket.listen(1)
	
	while True:
		conn, addr = server_socket.accept()
		# print("hello, there" + str(addr))
		logger.info('connected from ' + str(addr))
		
		while True:
			message = conn.recv(1024).decode("UTF-8")
			print("received from client: " + message)
			command = json.loads(message)
			print("command is: " + command['cmd'] + " and parameter is: " + command['parameter'])
			result = get_info()
			if result:
				try:
					conn.sendall(message.encode("UTF-8"))
				except:
					logger.error('send status back failed, connection error')
				finally:
					conn.close()
					break

def get_info():
	return True

if __name__ == '__main__':
	windows_server()