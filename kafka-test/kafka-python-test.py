#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 由于 windows 上不能安装 confluent-kafka-python，所以只能用 kafka-python 向 kafka 生产数据，生产相对简单一些
# producer
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='kafka01:9092')
future = producer.send('test', b'message_1 to topic test', partition=3)
future = producer.send('test', 'message_2 to topic test'.encode('UTF-8'), partition=3)
result = future.get(timeout=5)
print(result)


# consumer
from kafka import KafkaConsumer
from kafka import TopicPartition

consumer = KafkaConsumer(bootstrap_servers='kafka01:9092')
consumer = KafkaConsumer('test', bootstrap_servers='kafka01:9092', group_id='group1')

consumer = KafkaConsumer(bootstrap_servers='kafka01:9092', group_id='group2')
consumer.assign([TopicPartition('test', 2)])
for msg in consumer:
	print (msg)