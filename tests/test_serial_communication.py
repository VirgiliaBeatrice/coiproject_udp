#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial
import threading
import time
import random

from coiproject_lapissensor.log_instance import log_instance


HEX_DICT = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "A", "B", "C", "D", "E", "F"
]

EVENTS = [
    u"Return Dev Info",
    u"Return "
]


class SerialCommunicationThread(threading.Thread):

    def __init__(self, port, sending_interval):
        super(SerialCommunicationThread, self).__init__()
        self.ser = serial.Serial(port, baudrate=57600)
        self.sending_interval = sending_interval / 1000.0
        self.stop_flag = True
        self.logger = log_instance.Logger(
            logname=u"log.txt",
            loglevel=1,
            logger=u"SerialInfoLog").get_log()

        self.ser.flushInput()

    def open(self):
        try:
            self.ser.open()
        except (OSError, serial.SerialException):
            self.ser.close()
            self.ser.open()

        self.stop_flag = False

    def close(self):
        self.stop_flag = True
        time.sleep(1)
        self.ser.close()

    def receive_data(self):
        rev_data = self.ser.read(self.ser.in_waiting)
        self.logger.info(u"Receive: " + rev_data[:-1])
        return rev_data

    # TODO(Haoyan.Li): Finish this analysis code.
    @staticmethod
    def _analysis_data(rev_data):
        if u"ATA" in rev_data:
            event_code = 1
        elif u"AT$W0B07=0100" in rev_data:
            event_code = 2
        elif u"AT$W0B07=0000" in rev_data:
            event_code = 3
        else:
            event_code = 0

        return event_code

    def send_msg(self, msg):
        self.ser.write(msg.encode(u"utf-8"))
        self.logger.info(u"Send: " + msg[:-2])

    def _generate_random_data(self, bits):
        seq = []
        for idx in range(bits):
            seq.append(random.choice(HEX_DICT))
        # print seq
        # print u"0x" + u"".join(seq)
        msg = u"N  OK   0x0B06 VALUE:0x" + u"".join(seq) + u"\r\n\r\n"
        self.logger.info(u"Send: Data - " + msg[:-2])
        return msg

    def run(self):
        while not self.stop_flag:
            self.ser.write(self._generate_random_data(40).encode())
            time.sleep(self.sending_interval)
        pass

# N  OK   0x0B06 VALUE:0xF0FF44DA030064FD01FF0BFC6600EBFF87FF88C7


if __name__ == '__main__':
    port = raw_input(u"Please input port: ").encode()
    mode = raw_input(u"Please input mode: ")

    if int(mode) == 1:
        msg = u"1 0xF5A8F13D5E7C -070 LAPIS_RAW0 \r\n\r\n"
    elif int(mode) == 2:
        msg = u"1 0xE9A8F13D5E7C -070 LAPIS_RAW1 \r\n\r\n"
    else:
        msg = u"1 0xD9A8F13D5E7C -070 LAPIS_RAW2 \r\n\r\n"

    thread = SerialCommunicationThread(port, 20)
    thread.open()

    flag = True
    # while flag:
    #     thread.

    raw_input(u"Waiting...")
    thread.receive_data()
    thread.send_msg(msg)

    raw_input(u"Waiting...")
    thread.receive_data()
    thread.send_msg(u"CONNECT\r\n")

    raw_input(u"Waiting...")
    thread.receive_data()
    thread.send_msg(u"W  OK   0x0B07\n" +
                    u"OK\r\n")

    thread.start()
    raw_input()
    # print thread.isAlive()

    thread.close()
