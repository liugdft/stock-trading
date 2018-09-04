#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, logging, json, time, atexit
import pandas as pd
import win32api, win32con
from kafka import KafkaProducer

# socket_server 端口
host = ('0.0.0.0', 10000)

# 初始化日志信息
log_file = r'C:\Users\LiuGDFT\Desktop\stock-data\stock-windows.log'
logger = logging.getLogger("windows-server")
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

# 初始化虚拟键盘的代码
VK_CODE = {
	'backspace':0x08,
	'tab':0x09,
	'clear':0x0C,
	'enter':0x0D,
	'shift':0x10,
	'ctrl':0x11,
	'alt':0x12,
	'pause':0x13,
	'caps_lock':0x14,
	'esc':0x1B,
	'spacebar':0x20,
	'page_up':0x21,
	'page_down':0x22,
	'end':0x23,
	'home':0x24,
	'left_arrow':0x25,
	'up_arrow':0x26,
	'right_arrow':0x27,
	'down_arrow':0x28,
	'select':0x29,
	'print':0x2A,
	'execute':0x2B,
	'print_screen':0x2C,
	'ins':0x2D,
	'del':0x2E,
	'help':0x2F,
	'0':0x30,
	'1':0x31,
	'2':0x32,
	'3':0x33,
	'4':0x34,
	'5':0x35,
	'6':0x36,
	'7':0x37,
	'8':0x38,
	'9':0x39,
	'a':0x41,
	'b':0x42,
	'c':0x43,
	'd':0x44,
	'e':0x45,
	'f':0x46,
	'g':0x47,
	'h':0x48,
	'i':0x49,
	'j':0x4A,
	'k':0x4B,
	'l':0x4C,
	'm':0x4D,
	'n':0x4E,
	'o':0x4F,
	'p':0x50,
	'q':0x51,
	'r':0x52,
	's':0x53,
	't':0x54,
	'u':0x55,
	'v':0x56,
	'w':0x57,
	'x':0x58,
	'y':0x59,
	'z':0x5A,
	'numpad_0':0x60,
	'numpad_1':0x61,
	'numpad_2':0x62,
	'numpad_3':0x63,
	'numpad_4':0x64,
	'numpad_5':0x65,
	'numpad_6':0x66,
	'numpad_7':0x67,
	'numpad_8':0x68,
	'numpad_9':0x69,
	'multiply_key':0x6A,
	'add_key':0x6B,
	'separator_key':0x6C,
	'subtract_key':0x6D,
	'decimal_key':0x6E,
	'divide_key':0x6F,
	'F1':0x70,
	'F2':0x71,
	'F3':0x72,
	'F4':0x73,
	'F5':0x74,
	'F6':0x75,
	'F7':0x76,
	'F8':0x77,
	'F9':0x78,
	'F10':0x79,
	'F11':0x7A,
	'F12':0x7B,
	'F13':0x7C,
	'F14':0x7D,
	'F15':0x7E,
	'F16':0x7F,
	'F17':0x80,
	'F18':0x81,
	'F19':0x82,
	'F20':0x83,
	'F21':0x84,
	'F22':0x85,
	'F23':0x86,
	'F24':0x87,
	'num_lock':0x90,
	'scroll_lock':0x91,
	'left_shift':0xA0,
	'right_shift ':0xA1,
	'left_control':0xA2,
	'right_control':0xA3,
	'left_menu':0xA4,
	'right_menu':0xA5,
	'browser_back':0xA6,
	'browser_forward':0xA7,
	'browser_refresh':0xA8,
	'browser_stop':0xA9,
	'browser_search':0xAA,
	'browser_favorites':0xAB,
	'browser_start_and_home':0xAC,
	'volume_mute':0xAD,
	'volume_Down':0xAE,
	'volume_up':0xAF,
	'next_track':0xB0,
	'previous_track':0xB1,
	'stop_media':0xB2,
	'play/pause_media':0xB3,
	'start_mail':0xB4,
	'select_media':0xB5,
	'start_application_1':0xB6,
	'start_application_2':0xB7,
	'attn_key':0xF6,
	'crsel_key':0xF7,
	'exsel_key':0xF8,
	'play_key':0xFA,
	'zoom_key':0xFB,
	'clear_key':0xFE,
	'+':0xBB,
	',':0xBC,
	'-':0xBD,
	'.':0xBE,
	'/':0xBF,
	'`':0xC0,
	';':0xBA,
	'[':0xDB,
	'\\':0xDC,
	']':0xDD,
	"'":0xDE,
	'`':0xC0}

# 初始化到 kafka 的连接
producer = KafkaProducer(bootstrap_servers='Node1:9092')

# 初始化 socket server
server_socket = socket.socket()
server_socket.bind(host)
server_socket.listen(1)
	
def clean_atexit():
	conn.close()

def windows_server():
	while True:
		conn, addr = server_socket.accept()
		logger.info("received connection from client: " + str(addr))
		message = conn.recv(1024).decode("UTF-8")
		logger.info("received command from client: " + message)
		command = json.loads(message)
		# print("command is: " + command['command'] + " and parameter is: " + command['parameter'])
		result = get_stockinfo(command)
		if result:
			try:
				conn.sendall(str(result).encode("UTF-8"))
			except:
				logger.error('send result back failed, connection error')
			finally:
				conn.close()
		else:
			try:
				conn.sendall(str(result).encode("UTF-8"))
			except:
				logger.error('get stock info failed')
			finally:
				conn.close()

def get_stockinfo_test(command):
	if command['parameter']['sort_by'] == "rise_ratio":
		return "sort_by_rise_ratio"
	elif command['parameter']['sort_by'] == "volume":
		return "sort_by_volume"
	else:
		return False
	
def get_stockinfo(command):
	# 按照涨幅来排序效果并不好，只按照成交量排序，然后涨幅可以自己计算，会更快一下
	# if command['parameter']['sort_by'] == "rise_ratio":
		# 东方财富全景图 涨幅% 的点击位置
		# cursor_position = (417, 85)
		# partition_num = 0
	# elif command['parameter']['sort_by'] == "volume":
		# 东方财富全景图 总量 的点击位置
		# cursor_position = (547, 85)
		# partition_num = 1
	# else:
		# return False
	# 调试获取鼠标指针位置
	# win32api.GetCursorPos()
	cursor_position = (547, 85)
	partition_num = 0
	# 点击按照某项指标排序
	win32api.SetCursorPos(cursor_position)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
	time.sleep(1)

	# 右键，导出数据到文件
	win32api.SetCursorPos((417, 105))
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
	time.sleep(0.6)

	# 数据导出
	win32api.SetCursorPos((518, 258))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
	time.sleep(0.6)

	# 导出全部数据
	win32api.SetCursorPos((677, 261))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
	time.sleep(1.4)

	# 下一步，下一步，然后完成
	win32api.SetCursorPos((1040, 638))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
	time.sleep(0.5)
	win32api.SetCursorPos((1040, 638))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
	time.sleep(1)
	win32api.SetCursorPos((1040, 638))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
	time.sleep(0.2)

	# 每次下载完成后，点击 代码 位置归位，方便下一次可以点击任何一个指标
	# 东方财富全景图 代码 的点击位置
	return_position = (142, 85)
	win32api.SetCursorPos(return_position)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
	
	# 记录数据生成的时间，用于存储到 influxdb
	timestamp = time.time_ns()
	
	# 查看单只股票
	# str = "00011"
	# for c in str:
		# win32api.keybd_event(VK_CODE[c],0,0,0)
		# win32api.keybd_event(VK_CODE[c],0,win32con.KEYEVENTF_KEYUP,0)
		# time.sleep(0.5)
	# win32api.keybd_event(VK_CODE['enter'],0,0,0)
	# win32api.keybd_event(VK_CODE['enter'],0,win32con.KEYEVENTF_KEYUP,0)
	# time.sleep(0.5)
	
	# 左右键移动
	# for i in range(100):
		# win32api.keybd_event(VK_CODE['left_arrow'],0,0,0)
		# win32api.keybd_event(VK_CODE['left_arrow'],0,win32con.KEYEVENTF_KEYUP,0)
		# time.sleep(0.5)
		
	# 读取文件内容，转化为 pandas 数据
	file = r'C:\Users\LiuGDFT\Desktop\Table.xls'
	
	# 跳过原来的列名
	# stock_sortdata = pd.read_csv(file, header=None, sep='	', encoding="gbk", skiprows=[0])
	# 取新的列名
	# stock_sortdata = pd.read_csv(file, header=None, sep='	', encoding="gbk", skiprows=[0], names=['No.', 'stock_id', ...])
	# 也可以保留原来的列名为数据列名，是中文的
	stock_sortdata = pd.read_csv(file, sep='	', encoding="gbk")
	
	# 最后一列为无效的空数据，删除最后一列
	stock_sortdata = stock_sortdata.drop(["Unnamed: 21"], axis = 1)
	
	# 代码列原来的值是 = "00001"，处理成 HK.00001 这样的格式
	stock_sortdata["代码"] = stock_sortdata["代码"].map(lambda x: "HK." + x.lstrip('= "').rstrip('"'))
	
	# 转换为 json 格式，便于传输和存储
	stock_sortdata_json = stock_sortdata.to_json()
	
	# 和 timestamp 等信息一起组成最终要传送的data
	final_data = {"timestamp":timestamp, "data_source":"eastmoney", "stock_plate":command['parameter']['stock_plate'], "sort_by":command['parameter']['sort_by'], "data":stock_sortdata_json}
	final_data_stream = json.dumps(final_data)
	
	# 把内容发送到 kafka
	try:
		future = producer.send('eastmoney', final_data_stream.encode('UTF-8'), partition=partition_num)
		result = future.get(timeout=5)
	except:
		logger.error('send final_data_stream to kafka failed')
		return False
	else:
		logger.info('sent final_data_stream to kafka')
		return True

if __name__ == '__main__':
	atexit.register(clean_atexit)
	windows_server()