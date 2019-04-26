#!/usr/local/bin/python
# coding:utf-8

from des_cracker import config_master
import socket
import json
from DES.des_algorithm import *

class client:
    def __init__(self, max_data_size, key, plain_text):
        self.max_data_size = max_data_size
        self.node_info = config_master.nodes
        self.node_list = config_master.nodes_list
        self.server_map = dict()
        self.initial()
        self.key = key
        self.plain_text = plain_text
        self.encrypt()


    def initial(self):
        for node_name in self.node_info:
            print(node_name)
            self.server_map[node_name] = None
            host_ip = self.node_info[node_name]["ip"]
            host_port = self.node_info[node_name]["port"]
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_map[node_name] = send_socket
            send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            send_socket.connect((host_ip, int(host_port)))

            print('connected with master:', node_name, host_ip, host_port)


    def encrypt(self):
        d = des()
        r = d.encrypt(key, text)
        self.cipher = ' '.join(format(ord(x), 'b') for x in r)
        self.recover = d.decrypt(key, r)

    def send_cipher(self):
        cipher = dict()
        cipher['cipher'] = self.cipher
        # master = self.node_list[0]
        cipher_encode = json.dumps(cipher).encode('utf-8')
        self.server_map[0].sendall(cipher_encode)
        while True:
            res = self.server_map[0].recv(self.max_data_size)
            by = b''
            by += res
            data = json.loads(by.decode("utf-8"))
            if data["succ"] == "True":
                pred_key = data['pred_key']
                mes = {}
                mes['recv'] = "True"
                mes['finished'] = "False"
                mes = json.dumps(mes).encode('utf-8')
                self.server_map[0].sendall(mes)
                if pred_key == self.key:
                    print(pred_key)
                    print('finished')
                    break

        mes_fin = {}
        mes_fin['finised'] = "True"
        mes_fin = json.dumps(mes_fin).encode('utf-8')
        self.server_map[0].sendall(mes_fin)


if __name__ == '__main__':
    client_ = client(1024, "ningfeiw", "Hello wo")