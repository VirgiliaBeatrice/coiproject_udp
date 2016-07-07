#!/usr/bin/env python
# -*- coding:utf8 -*-

import socket
import json

FILE_NAME = u"config.json"
MESSAGE = "Hello, World!"


def load_config():
    """ Loading a pre-defined configuration file.

    :return: configuration values[Dict]
    """
    with open(FILE_NAME) as f:
        config = json.load(f)

    return config


class UdpSender:
    def __init__(self, udp_ip, udp_port):
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_DGRAM)
        self.udp_ip = udp_ip
        self.udp_port = udp_port

    def send_msg(self, msg):
        self.socket.sendto(msg, (self.udp_ip, self.udp_port))


if __name__ == '__main__':
    cfg = load_config()
    print cfg
    ip = cfg[u"IP_Address"]
    port = cfg[u"Port"]

    print "UDP target IP:", ip
    print "UDP target port:", port
    print "message:", MESSAGE

    udp_sender = UdpSender(ip, port)
    udp_sender.send_msg(MESSAGE)
