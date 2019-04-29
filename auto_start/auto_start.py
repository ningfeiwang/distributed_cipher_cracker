#!/usr/local/bin/python
# coding:utf-8

import os
import appscript
import des_cracker.config_nodes as config
import time

#
for node in config.nodes_list:
    cmd = "ssh niw217@" + config.nodes[node]["ip"] + " 'python2.7 -u ~/des_cracker/server_node.py "  + node + " 1024 > " + node + ".log'"
    print(cmd)
    appscript.app('Terminal').do_script(cmd)

time.sleep(10)
#
# for node in config.nodes_list:
#     cmd = "ssh niw217@" + config.nodes[node]["ip"] + " 'python ~/new/client.py 4000 10 2' "
#     print(cmd)
#     appscript.app('Terminal').do_script(cmd)