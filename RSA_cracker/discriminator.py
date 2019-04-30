#!/usr/local/bin/python
# coding:utf-8

import sys

import config_nodes as config
import socket
import json
import threading
# from DES.des_algorithm import *
# import b2s
import numpy as np
import os


def binaryToDecimal(binary):
    # binary1 = binary
    decimal, i, n = 0, 0, 0
    # print(len(binary))
    binary = binary[::-1]
    for i in range(len(binary)):
        # print(int(binary[i]))
        dec = int(binary[i]) % 10
        # print(dec)
        decimal += dec * pow(2, i)
    print(decimal)
    return decimal

class server_nodes:
    def __init__(self, server_name, max_data_size):
        self.max_data_size = max_data_size
        self.connections = []
        self.node_info = config.nodes
        self.node_list = config.nodes_list
        self.server_name = server_name
        # self.d = des()
        self.initial()
        self.succ = 0
        self.buffer = []
        self.lock = threading.Lock()
        self.thread_processing = threading.Thread(target=self.thread_processing)
        self.thread_processing.daemon = True
        self.thread_processing.start()

    def thread_processing(self):
        while True:
            if self.succ == 1:
                break
            if self.buffer != []:
                print(22222)
                self.lock.acquire()
                copime = self.buffer[:]
                self.buffer = []
                self.lock.release()
            else:
                continue

            for i in copime:
                if int(i) == int(self.pri_key):
                    print('finished')
                    self.succ = 1
            if self.succ == 1:
                print('finish')
                break
    #
    # def thread_receiving(self):
    #     while True:
    #         res = self.server_map_nodes['discriminator'].recv(self.max_data_size)
    #         by = b''
    #         by += res
    #         data = json.loads(by.decode("utf-8"))
    #         if data['succ'] == True:
    #             self.succ = 1
    #             break

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

    def main(self, s_res, tmp_key_con, k_con, conn):
        left = s_res[0]
        right = s_res[1]
        flag = 0

        print('left', left)
        print('right', right)
        while left <= right:
            # print(left)
            # if self.succ == 1:
            #     break
            # key_bin = '{:064b}'.format(left)
            # print('key_bin', key_bin)
            # print('k_con', k_con)
            if k_con == left:
                flag = 1
                self.succ = 1
                break
            left += 1

        if flag == 0:
            data = {}
            data['succ'] = "False"
            data['pred_key'] = left
            print('fail')
            mes = json.dumps(data).encode('utf-8')
            conn.sendall(mes)
        else:
            data = {}
            data['succ'] = "True"
            data['pred_key'] = tmp_key_con
            print('succeed')
            mes = json.dumps(data).encode('utf-8')
            conn.sendall(mes)


    def split_thread(self, l, r):
        map_ = dict()
        length = 8
        block_size = (r - l) / length
        for i in range(length):
            if i < length - 1:
                map_[i] = [l + i * block_size, l + (i + 1) * block_size]
            else:
                map_[i] = [l + i * block_size, r]
        print ('map_', map_)
        return map_

    def processing(self, conn, addr):
        while True:
            data_re = conn.recv(self.max_data_size)
            if not data_re:
                break
            by = b''
            by += data_re
            data = json.loads(by.decode("utf-8"))
            print("data", data)
            self.pri_key = data['private']
            copime = data['copime']

            self.lock.acquire()
            # print(11111)
            self.buffer += copime
            self.lock.release()
            # print(self.buffer)


            if self.succ == 1:
                data = {}
                print('finished')
                data['succ'] = "True"
                data['pred_key'] = self.pri_key
                print('succ')
                mes = json.dumps(data).encode('utf-8')
                conn.sendall(mes)




            # for i in copime:
            #     if int(i) == int(self.pri_key):
            #         data = {}
            #         data['succ'] = "True"
            #         data['pred_key'] = i
            #         print('succ')
            #         mes = json.dumps(data).encode('utf-8')
            #         conn.sendall(mes)
            #         self.succ = 1
            # if self.succ == 1:
            #     print('finish')
            #     break

    def server_start(self):
        while True:
            conn, addr = self.server_map[self.server_name].accept()
            print("connect with ", conn)
            new_thread = threading.Thread(target = self.processing, args = (conn, addr))
            new_thread.daemon = True
            new_thread.start()

if __name__ == '__main__':
    # print(len('0111001101100101011000110111001000000000000000000000000000000000'))
    # binaryToDecimal('0111001101100101011000110111001000000000000000000000000000000000')
    global_var = 0
    server = server_nodes(sys.argv[1], int(sys.argv[2]))
    server.server_start()