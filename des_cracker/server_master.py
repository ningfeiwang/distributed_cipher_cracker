#!/usr/local/bin/python
# coding:utf-8

import sys

import des_cracker.config_master as config
# import RHT
import socket
import json
import threading
import os


class server_nodes:
    def __init__(self, server_name, max_data_size):
        self.max_data_size = max_data_size
        self.server_name = server_name
        self.node_info = config.nodes
        self.node_list = config.nodes_list
        self.server_map_nodes = dict()
        self.server_map_client = dict()
        self.initial_listen()
        self.initial_connection()

    def initial_connection(self):
        for node_name in self.node_info:
            print(node_name)
            self.server_map_nodes[node_name] = None
            host_ip = self.node_info[node_name]["ip"]
            host_port = self.node_info[node_name]["port"]
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_map_nodes[node_name] = send_socket
            send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            send_socket.connect((host_ip, int(host_port)))

            print('connected with nodes:', node_name, host_ip, host_port)

    def initial_listen(self):
        for node_name in self.node_info:
            self.server_map_client[node_name] = None
            host_ip = self.node_info[node_name]["ip"]
            host_port = self.node_info[node_name]["port"]
            if node_name == self.server_name:
                self.server_map_client[node_name] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_map_client[node_name].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # print(host_ip)
                self.server_map_client[node_name].bind((host_ip, int(host_port)))
                self.server_map_client[node_name].listen(5)
                print("server starts")
                print("ip and port: " + host_ip + ":" + host_port)

    def assign_split(self, range_):
        map_ = dict()
        length = len(self.node_list)
        block_size = range_ / length
        for i in range(length):
            if i < length - 1:
                map_[self.node_list[i]] = [i * block_size, (i + 1) * block_size]
            else:
                map_[self.node_list[i]] = [i * block_size, length]
        return map_

    def handling(self, conn, cipher, range_, server_name):
        while True:
            mes = {}
            mes['range_'] = range_
            mes['cipher'] = cipher
            mes = json.dumps(mes).encode('utf-8')
            self.server_map[server_name].sendall(mes)
            res = self.server_map[server_name].recv(self.max_data_size)
            by = b''
            by += res
            data = json.loads(by.decode("utf-8"))
            if data['succ'] == "True":
                key = data['key']
            conn.sendall(res)
            # res = conn.recv(self.max_data_size)
            # by = b''
            # by += res
            # data = json.loads(by.decode("utf-8"))
            # if data['finished'] == "True":
            #     mes = {}
            #     mes['finished'] = "True"
            #     mes = json.dumps(mes).encode('utf-8')
            #     for server_ in self.node_info:
            #         if server_ != server_name:
            #             self.server_map_nodes[server_].sendall(mes)
            #     break

    def processing(self, conn, addr):
        while True:
            data_re = conn.recv(self.max_data_size)
            if not data_re:
                break
            by = b''
            by += data_re
            data = json.loads(by.decode("utf-8"))
            print("data", data)
            if data['finished'] == "True":
                mes = {}
                mes['finished'] = "True"
                mes = json.dumps(mes).encode('utf-8')
                for server_ in self.node_info:
                    if server_ != self.server_name:
                        self.server_map_nodes[server_].sendall(mes)
                break
            cipher = data['cipher']
            assign_map = self.assign_split(64)
            thread_list = []
            for i in range(len(self.node_list)):
                thread_list.append(threading.Thread(target=self.handling), args = (conn, cipher, assign_map[self.node_list[i]], self.node_list[i]))
                thread_list[i].daemon = False
            for i in range(len(self.node_list)):
                thread_list[i].start()


    def server_start(self):
        while True:
            conn, addr = self.server_map[self.server_name].accept()
            print("connect with ", conn)
            new_thread = threading.Thread(target = self.processing, args = (conn, addr))
            new_thread.daemon = True
            new_thread.start()

if __name__ == '__main__':
    global_var = 0
    server = server_nodes(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    server.server_start()