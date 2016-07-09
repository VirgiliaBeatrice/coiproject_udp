#!/usr/bin/env python
# -*- coding:utf8 -*-

import socket
import json
import loginstance

FILE_NAME = u"config.json"
MESSAGE = "Hello, World!"


# def load_config():
#     """ Loading a pre-defined configuration file.
#
#     :return: configuration values[Dict]
#     """
#     with open(FILE_NAME) as f:
#         config = json.load(f)
#
#     return config


class UdpClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_DGRAM)
        self._load_config()
        self.udp_ip = self.config[u"IP_Address"]
        self.udp_port = self.config[u"Port"]

    def send_msg(self, msg):
        self.socket.sendto(msg, (self.udp_ip, self.udp_port))

    def _load_config(self):
        with open(FILE_NAME) as f:
            self.config = json.load(f)


if __name__ == '__main__':
    # cfg = load_config()
    # print cfg
    # ip = cfg[u"IP_Address"]
    # port = cfg[u"Port"]

    # print "UDP target IP:", ip
    # print "UDP target port:", port
    # print "message:", MESSAGE

    # udp_sender = UdpClient()
    # udp_sender.send_msg(MESSAGE)
    logger = loginstance.Logger(
        logname=u"udp_log",
        loglevel=1,
        logger=u"UDPServerLog").getlog()

    UDP_IP = "127.0.0.1"
    UDP_PORT = 4444

    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        logger.info(data)
        # print "received message:", data
