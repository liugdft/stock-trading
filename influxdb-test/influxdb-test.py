#!/usr/bin/env python
# -*- coding: utf-8 -*-

from influxdb import InfluxDBClient
import time

db = "test"
json_body = [
    {
        "measurement": "cpu_load_short",
        "tags": {
            "host": "server01",
            "region": "us-west"
        },
        "time": time.time_ns(),
        "fields": {
            "value": 0.64
        }
    }
]

client = InfluxDBClient('192.168.100.44', 8086)
client.write_points(json_body, database=db)
result = client.query('select * from cpu_load_short;', database=db)
print("Result: {0}".format(result))