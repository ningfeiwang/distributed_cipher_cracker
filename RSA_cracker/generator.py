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
from collections import deque
import subprocess
import time

def write_log(message):
    global global_var
    _sequence = global_var
    global_var += 1
    with open('/home/niw217/new/log/fail.log', 'a') as file:
        file.write(str(_sequence) + '\n')
        file.write(message)
        file.write('\n')


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
        self.fail = deque([])
        self.contribution = dict()
        # self.thread_fail = threading.Thread(target=self.checking)
        # self.thread_fail.daemon = True
        # self.thread_fail.start()
        self.thread_receiving = threading.Thread(target=self.thread_receiving)
        self.thread_receiving.daemon = False
        self.thread_receiving.start()

    def thread_receiving(self):
        while True:
            # print(1111)
            res = self.server_map_nodes['discriminator'].recv(self.max_data_size)
            by = b''
            by += res
            data = json.loads(by.decode("utf-8"))
            if data['succ'] == "True":
                self.succ = 1
                print('receiving finished')
                break


    def checking(self):
        while True:
            stop_sign = 0
            for node in self.node_list:
                host_ip = self.node_info[node]["ip"]
                res = subprocess.call(['ping', '-c', '3', host_ip])
                if res == 0:
                    continue
                else:
                    if self.contribution[node]:
                        continue
                    self.fail.append(node)
                    write_log(node)

            if len(self.contribution.keys()) != len(self.node_list):
                continue
            else:
                for node in self.contribution:
                    if self.contribution[node]:
                        stop_sign = 1
                        continue
                    else:
                        stop_sign = 0
                        break
            if stop_sign == 1:
                break

    def initial_connection(self):
        for node_name in self.node_info:
            print(node_name)
            if node_name == self.server_name:
                continue
            self.server_map_nodes[node_name] = None
            host_ip = self.node_info[node_name]["ip"]
            host_port = self.node_info[node_name]["port"]
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_map_nodes[node_name] = send_socket
            send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            send_socket.connect((host_ip, int(host_port)))

            print('connected with nodes:', node_name, host_ip, host_port)

    def check_coprime(self, x, y):
        if x == 1 and y == 1:
            return True
        elif x < 0 or y < 0 or x == y:
            return False
        elif x == 1 or y == 1:
            return True
        else:
            tmp = 0
            while True:
                tmp = x % y
                if tmp == 0:
                    break
                else:
                    x = y
                    y = tmp
            if y == 1:
                return True
            else:
                return False

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
                self.server_map_client[node_name].listen(5)
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
            self.contribution[server_name] = False
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
            self.contribution[server_name] = True
            if data['succ'] == "True":
                # self.contribution[server_name] = True
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
            num = 0
            copime = []
            while True:
                self.key_pub = int(data['key_pub'])
                if self.check_coprime(num, self.key_pub):
                    copime.append(num)
                num += 1
                if len(copime) == 100:
                    time.sleep(0.5)
                    mes = {}
                    mes['copime'] = copime
                    mes['private'] = data['key_pri']
                    self.key_pri = data['key_pri']
                    mes = json.dumps(mes).encode('utf-8')
                    self.server_map_nodes['discriminator'].sendall(mes)
                    copime = []
                if self.succ == 1:
                    print('finish')
                    break
            data = {}
            # print('finished')
            data['succ'] = "True"
            data['pred_key'] = self.key_pri
            print('succ')
            mes = json.dumps(data).encode('utf-8')
            conn.sendall(mes)



            # data_re = conn.recv(self.max_data_size)
            # if not data_re:
            #     break
            # by = b''
            # by += data_re
            # data = json.loads(by.decode("utf-8"))
            # print("data", data)
            # if data['finished'] == "True":
            #     mes = {}
            #     mes['finished'] = "True"
            #     mes = json.dumps(mes).encode('utf-8')
            #     for server_ in self.node_info:
            #         if server_ != self.server_name:
            #             self.server_map_nodes[server_].sendall(mes)
            #     break
            # cipher = data['cipher']
            # key = data['key']
            # assign_map = self.assign_split(64)
            # thread_list = []
            # for i in range(len(self.node_list)):
            #     thread_list.append(threading.Thread(target=self.handling, args = (conn, cipher, assign_map[self.node_list[i]], self.node_list[i], key)))
            #     thread_list[i].daemon = False
            # for i in range(len(self.node_list)):
            #     thread_list[i].start()


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