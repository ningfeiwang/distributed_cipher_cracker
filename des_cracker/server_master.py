#!/usr/local/bin/python
# coding:utf-8

import sys

import config_nodes
# import RHT
import config_master
import socket
import json
import threading
import os


class server_nodes:
    def __init__(self, server_name, max_data_size):
        self.max_data_size = max_data_size
        self.server_name = server_name
        self.node_info = config_nodes.nodes
        self.node_list = config_nodes.nodes_list
        self.server_map_nodes = dict()
        self.master_info = config_master.nodes
        self.master_list = config_master.nodes_list
        self.server_map_client = dict()
        self.initial_listen()
        self.initial_connection()
        self.succ = 0

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
        for node_name in self.master_info:
            self.server_map_client[node_name] = None
            host_ip = self.master_info[node_name]["ip"]
            host_port = self.master_info[node_name]["port"]
            if node_name == self.server_name:
                self.server_map_client[node_name] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_map_client[node_name].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # print(host_ip)
                self.server_map_client[node_name].bind((host_ip, int(host_port)))
                self.server_map_client[node_name].listen(80)
                print("server starts")
                print("ip and port: " + host_ip + ":" + host_port)

    def assign_split(self, range_):
        map_ = dict()
        range_ -= 1
        length = len(self.node_list)
        block_size = (18446744073709551616 - 0) / length
        for i in range(length):
            if i < length - 1:
                map_[self.node_list[i]] = [0 + i * block_size, 0 + (i + 1) * block_size]
            else:
                map_[self.node_list[i]] = [0 + i * block_size, 18446744073709551616]
        print ('map_', map_)
        return map_
    # def assign_split(self, range_):
    #     map_ = dict()
    #     range_ -= 1
    #     length = len(self.node_list)
    #     block_size = (8315161632581877759 - 8315161628286910464) / length
    #     for i in range(length):
    #         if i < length - 1:
    #             map_[self.node_list[i]] = [8315161628286910464 + i * block_size, 8315161628286910464 + (i + 1) * block_size]
    #         else:
    #             map_[self.node_list[i]] = [8315161628286910464 + i * block_size, 8315161632581877759]
    #             8315161629989035883
    #     print ('map_', map_)
    #     return map_

    def handling(self, conn, cipher, range_, server_name, key):
        while True:
            mes = {}
            mes['left'] = range_[0]
            mes['right'] = range_[-1]

            mes['cipher'] = cipher
            mes['key'] = key
            mes = json.dumps(mes).encode('utf-8')
            self.server_map_nodes[server_name].sendall(mes)
            res = self.server_map_nodes[server_name].recv(self.max_data_size)
            by = b''
            by += res
            data = json.loads(by.decode("utf-8"))
            print(data)
            if data['succ'] == "True":
                mess = {}
                mess['succ'] = 'True'
                mess['pred_key'] = key
                # key = data['pred_key']
                mess = json.dumps(mess).encode('utf-8')
                conn.sendall(mess)
                print('send to client: ', mess)
                break
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
            key = data['key']
            assign_map = self.assign_split(64)
            thread_list = []
            for i in range(len(self.node_list)):
                thread_list.append(threading.Thread(target=self.handling, args = (conn, cipher, assign_map[self.node_list[i]], self.node_list[i], key)))
                thread_list[i].daemon = False
            for i in range(len(self.node_list)):
                thread_list[i].start()


    def server_start(self):
        while True:
            conn, addr = self.server_map_client[self.server_name].accept()
            print("connect with ", conn)
            new_thread = threading.Thread(target = self.processing, args = (conn, addr))
            new_thread.daemon = True
            new_thread.start()

if __name__ == '__main__':
    global_var = 0
    server = server_nodes(sys.argv[1], int(sys.argv[2]))
    server.server_start()