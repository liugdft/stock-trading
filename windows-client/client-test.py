#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, logging, json

def client_test():
    host = '192.168.100.251'
    port = 10000
    client_socket = socket.socket()
    client_socket.connect((host, port))
    message = input(" -> ")
    command = {"cmd":"get_info", "parameter":"hk_raise_rate"}
    cmd = json.dumps(command)

    while message.lower().strip() != 'bye':
        client_socket.sendall(cmd.encode("UTF-8"))
        recv_message = client_socket.recv(1024).decode("UTF-8")
        print("received from server: " + recv_message)
        message = input(" -> ")

    client_socket.close()

if __name__ == '__main__':
    client_test()
