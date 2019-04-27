#!/usr/local/bin/python
# coding:utf-8

import sys

import config_nodes as config
import socket
import json
import threading

import os



class server_nodes:
    def __init__(self, server_name, max_data_size):
        self.max_data_size = max_data_size
        self.node_info = config.nodes
        self.node_list = config.nodes_list
        self.server_name = server_name
        self.initial()

    def initial(self):
        self.server_map = dict()

        for node_name in self.node_info:
            self.server_map[node_name] = None
            host_ip = self.node_info[node_name]["ip"]
            host_port = self.node_info[node_name]["port"]
            if node_name == self.server_name:
                self.server_map[node_name] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                self.server_map[node_name].setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                # print(host_ip)
                self.server_map[node_name].bind((host_ip, int(host_port)))
                self.server_map[node_name].listen(5)
                print("server starts")
                print("ip and port: " + host_ip + ":" + host_port)


    def processing(self, conn, addr):
        while True:
            data_re = conn.recv(self.max_data_size)
            if not data_re:
                break
            by = b''
            by += data_re
            data = json.loads(by.decode("utf-8"))
            print("data", data)
            mes = {}
            mes['succ'] = "True"
            mes['pred_key'] = "secret_k"

            mes = json.dumps(mes).encode('utf-8')

            conn.sendall(mes)

    def server_start(self):
        while True:
            conn, addr = self.server_map[self.server_name].accept()
            print("connect with ", conn)
            new_thread = threading.Thread(target = self.processing, args = (conn, addr))
            new_thread.daemon = True
            new_thread.start()

if __name__ == '__main__':
    global_var = 0
    server = server_nodes(sys.argv[1], int(sys.argv[2]))
    server.server_start()