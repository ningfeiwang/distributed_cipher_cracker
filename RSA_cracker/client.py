#!/usr/local/bin/python
# coding:utf-8

import config_nodes
import socket
import json
import time

class client:
    def __init__(self, max_data_size, key_pub, key_pri, plain_text):
        self.max_data_size = max_data_size
        self.node_info = config_nodes.nodes
        self.node_list = config_nodes.nodes_list
        self.server_map = dict()
        self.initial()
        self.key_pub = key_pub
        self.key_pri = key_pri
        self.plain_text = plain_text
        self.encrypt_test()
        self.send_cipher()


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


    def encrypt_test(self):
        self.cipher = ''
        pass

    def send_cipher(self):
        cipher = dict()
        cipher['cipher'] = self.cipher
        cipher['finished'] = "False"
        cipher['key_pub'] = self.key_pub
        cipher['key_pri'] = self.key_pri
        # master = self.node_list[0]
        cipher_encode = json.dumps(cipher).encode('utf-8')
        self.server_map['generator'].sendall(cipher_encode)
        print('self.cipher',self.cipher)
        print('cipher_encode', cipher_encode)
        start = time.time()

        while True:
            # print(1111)
            res = self.server_map['generator'].recv(self.max_data_size)
            by = b''
            by += res
            data = json.loads(by.decode("utf-8"))
            if data["succ"] == "True":
                pred_key = data['pred_key']
                # mes = {}
                # mes['recv'] = "True"
                # mes['finished'] = "False"
                # mes = json.dumps(mes).encode('utf-8')
                # self.server_map[0].sendall(mes)
                if pred_key == self.key_pri:
                    print(pred_key)
                    print('finished')
                    break
        end = time.time()
        print('time: ', str(end - start))
        # mes_fin = {}
        # mes_fin['finished'] = "True"
        # mes_fin = json.dumps(mes_fin).encode('utf-8')
        # self.server_map[self.node_list[0]].sendall(mes_fin)


if __name__ == '__main__':
    client_ = client(1024, 9, 16, "Hello wo")