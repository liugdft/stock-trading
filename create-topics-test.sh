#!/usr/bin/env bash

# 为每一只 港股主板 的股票创建 1 个 topic，包含 10 个 partition
HK_main_plate_stocks=(
	"HK.00001"
	"HK.00002"
	"HK.00003"
	"HK.00004"
	"HK.00005"
	)

for stock in ${HK_main_plate_stocks[@]}
do
	echo ${stock}
	`kafka-topics --create --zookeeper localhost:2181 --replication-factor 1 --partitions 10 --topic ${stock}`
done