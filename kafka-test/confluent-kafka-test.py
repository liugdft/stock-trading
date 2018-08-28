#!/usr/bin/env python
# -*- coding: utf-8 -*-

from confluent_kafka import Producer
# 对于 producer 的要求：
# 指定 partition 生产信息；生产出错时报错。
def delivery_report(err, msg):
	""" Called once for each message produced to indicate delivery result.
		Triggered by poll() or flush(). """
	if err is not None:
		print('Message delivery failed: {}'.format(err))
	else:
		print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

producer = Producer({'bootstrap.servers': 'kafka01'})
producer.produce('test', 'message_2 to topic test from confluent_kafka'.encode('UTF-8'), partition=4, callback=delivery_report)
producer.flush()

import confluent_kafka
from confluent_kafka import Consumer, KafkaError
from confluent_kafka import TopicPartition
# 对于 consumer 的要求：
# 指定 partition 消费；同一个 group 的 consumer 断开后再连接，是否从上次消费断开的地方继续消费？；同一个 group 的 consumer 指定 partition 消费后，其他 partition 的默认 offset 在哪，还可以消费吗？；
# 从头开始消费；每次都消费最后一个 offset 的数据；按照 stock 数据的时间点保存 time、offset 的数组对，可以由某个时间点找到 offset，并从这个时间开始取数据

# auto.offset.reset，在没有 offset 位置记录时的位置重置动作，smallest, earliest, beginning 表示从开始消费， largest, latest, end 表示从最新的记录开始
# largest 的结果就是 [TopicPartition{topic=test,partition=3,offset=-1001,error=None}]
# Offset -1001 is a special value meaning Invalid or Default, depending on context.
# If you pass a TopicPartition list to assign() with offset set to -1001 it will attempt to fetch committed offsets from the broker, and if that fails revert to auto.offset.reset.
consumer = Consumer({
	'bootstrap.servers': 'kafka01',
	'group.id': 'temp',
	# 如果是临时需要跳跃 offset 访问其他位置的数据，则 auto.commit 设置为 False，auto.commit 设置为 True 适合正常订阅，断了也可以继续。
	# 在正常的订阅之外，如果要跳跃处理数据，则应该新建 group ，然后用 assign 来访问，同时设置 'enable.auto.commit': False 避免 offset 被记录；或者使用相同的 group，每次 close 后重连都从 commited offset 开始。
	'enable.auto.commit': False, 
	'default.topic.config': {
		'auto.offset.reset': 'smallest'
	}
})

# 消费整个 topic
# subscribe和assign是不能同时使用的。subscribe表示订阅topic，从kafka记录的offset开始消费。assign表示从指定的offset开始消费。
consumer.subscribe(['test'])

# 消费 topic 里某一个或几个特定的 partition
consumer.assign([TopicPartition('test', 4)])

# 重置 offset
consumer.assign([TopicPartition('test', 4, 2)])

# 获取一个 partition 的最小、最大 offset
consumer.get_watermark_offsets(TopicPartition('test', 4))
# （0, 19）

# 如果是一个新的 group.id 必须先消费一条消息，这样后面的重置 offset 才有效， 如果不消费，重置 offset 前后获取到的 offset 值都是-1001
# 获取当前 offset 位置
consumer.position([TopicPartition('test', 3)])

# 重置 offset 到任意位置，committed 决定了下一次连接后的 offset 位置（以 group 为维度），本次连接无效。本次连接的 offset 位置由 position 决定。
# 重置 offset 后，要 close 重新连才有效。position 决定本次连接的 offset 位置，用 seek() 修改。
consumer.seek(TopicPartition('test', 3, 1))
consumer.commit(offsets=[TopicPartition('test', 3, 7)])

# 检查重置的位置
msg = consumer.committed([TopicPartition('test', 3)])
print(msg)

# offset：Either an absolute offset (>=0) or a logical offset: OFFSET_BEGINNING, OFFSET_END, OFFSET_STORED, OFFSET_INVALID
while True:
	msg = consumer.poll(1.0)
	if msg is None:
		continue
	if msg.error():
		if msg.error().code() == KafkaError._PARTITION_EOF:
			continue
		else:
			print(msg.error())
			break
	print('Received message: {}'.format(msg.value().decode('utf-8')))

consumer.close()