#!/usr/bin/python
# -*- coding: utf-8 -*-

import struct
import threading
import time
import serial
# import logging

from coiproject_lapissensor.log_instance import log_instance
from coiproject_lapissensor.udp_client import udp_client


# TODO(Haoyan.Li): Need to be adjusted to current device id.
DEV_0 = u"F5"
DEV_1 = u"E9"
DEV_2 = u"D9"

DEVICES = {
    DEV_0: u"LAPIS_RAW0",
    DEV_1: u"LAPIS_RAW1",
    DEV_2: u"LAPIS_RAW2",
}


class SerialPort(threading.Thread):
    """Create a thread to open a serial port"""

    def __init__(self, port, baud_rate=57600, timeout=100):
        super(SerialPort, self).__init__()
        self.ser = serial.Serial(port, baud_rate)
        self.timeout = timeout / 1000
        self.udp_client = udp_client.UdpClient()
        self.device_code = u""
        self.stop_flag = True
        self.logger = log_instance.Logger(
            logname=u"Receive_log.txt",
            loglevel=1,
            logger=u"SerialInfoLog").get_log()
        self.ser.flushInput()

    def open(self):
        try:
            self.ser.open()
        except (OSError, serial.SerialException):
            self.ser.close()
            self.ser.open()

    def close(self):
        self.stop_flag = True
        time.sleep(1)
        self.ser.close()

    def _data_process(self):
        if self.ser.inWaiting() >= 65:
            # TODO(Haoyan.Li): Never use readline method.
            rev_data = self.ser.readline()

            if len(rev_data) == 65:
                pos = rev_data.find(u"VALUE:")
                if pos != -1:
                    self.logger.debug(rev_data)
                    msg = self._data_reformat(rev_data[(pos + 6):(pos + 48)])
                    self.udp_client.send_msg(msg)
            elif len(rev_data) == 2:
                pass
            else:
                self.logger.warn(u"Uncompleted data package has received.")
        else:
            pass

    def _data_reformat(self, hex_string):
        data_packet = [DEVICES[self.device_code[2:4]], u"00000"]
        offset = 2
        raw_data = struct.unpack(
            u"<9h1H",
            hex_string[offset:].encode(u"utf-8").decode(u"hex")
        )
        self.logger.debug(raw_data)

        idx = 0
        # for element in reversed(raw_data):
        # Little endian
        for element in raw_data:
            if idx in range(0, 3):
                processed_data = (float(element) / 1024.0) * 9.8
            elif idx in range(3, 6):
                processed_data = float(element) / 10.0
            elif idx in range(6, 9):
                processed_data = float(element) / 131.0
            else:
                # Change unit to hPa
                processed_data = float(element + 50000) / 100.0
            data_packet.append(str(processed_data).decode(u"utf-8"))

            idx += 1

        return_str = u" ".join(data_packet)
        self.logger.info(return_str)
        return return_str

    def send_cmd(self, cmd):
        self.ser.write((cmd + u"\r").encode(u"utf-8"))

    def receive_data(self):
        rev_cache = u""
        rev_data = []
        start_time = time.time()
        delta_time = 0

        while True:
            if self.ser.inWaiting() != 0:
                rev_cache += self.ser.read(
                    self.ser.inWaiting()).decode(u"utf-8")
            else:
                delta_time = time.time() - start_time

            if delta_time > self.timeout:
                # If function is None, the identity function is assumed,
                # that is, all elements of iterable that are false are removed.
                # Python will treat null string as False.
                rev_data.extend(
                    filter(None, rev_cache.splitlines()))

                if len(rev_data) >= 1:
                    for line in rev_data:
                        # print line.find(u"\n")
                        self.logger.debug(line)
                    return rev_data
                else:
                    raise SerialPortException(u"Cannot find any valid device.")

    def run(self):
        self.stop_flag = False
        while not self.stop_flag:
            self._data_process()


class SerialPortException(Exception):
    pass


def list_available_ports():
    """ List all available port names

        :return:
         A list of the serial ports now available on this system.
    """
    ports = [u"COM%s" % (i + 1) for i in range(16)]
    results = []

    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            results.append(port)
            print(u"Find {0} device.".format(port))
        except (OSError, serial.SerialException):
            pass

    return results


if __name__ == '__main__':
    # print time.time()
    pass

