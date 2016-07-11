#!/usr/bin/python
# -*- coding: utf-8 -*-

import struct
import threading
import time
import serial

from coiproject_lapissensor.log_instance import log_instance
from coiproject_lapissensor.udp_client import udp_client


# TODO(Haoyan.Li): Adjust to current device id.
DEV_0 = u"F5"
DEV_1 = u"E9"
DEV_2 = u"D9"

DEVICES = {
    DEV_0: u"LAPIS_RAW0",
    DEV_1: u"LAPIS_RAW1",
    DEV_2: u"LAPIS_RAW2",
}


class SerialPort(threading.Thread):

    def __init__(self, port, baud_rate=57600):
        super(SerialPort, self).__init__()
        self.ser = serial.Serial(port, baud_rate)
        self.udp_client = udp_client.UdpClient()
        self.device_code = u""
        self.stop_flag = True
        self.logger = log_instance.Logger(
            logname=u"Receive_log.txt",
            loglevel=1,
            logger=u"SerialInfoLog").get_log()
        # self.ser.reset_input_buffer()
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
        if self.ser.inWaiting() < 65:
            pass
        else:
            rev_data = self.ser.readline()
            # TODO(Haoyan.Li): Add a validation function.
            # pos = rev_data.find(u"VALUE:")
            # if pos != -1:
            #     msg = self._data_reformat(rev_data[(pos + 6):(pos + 48)])
            #     self.udp_client.send_msg(msg)

            if len(rev_data) == 65:
                # logger.info(rev_data[:-2])
                pos = rev_data.find(u"VALUE:")
                if pos != -1:
                    msg = self._data_reformat(rev_data[(pos + 6):(pos + 48)])
                    self.udp_client.send_msg(msg)
            elif len(rev_data) == 2:
                pass
            else:
                self.logger.info(u"Uncompleted data package has received.")

    @staticmethod
    def _half_to_float(h):
        s = int((h >> 15) & 0x00000001)  # sign
        e = int((h >> 10) & 0x0000001f)  # exponent
        f = int(h & 0x000003ff)  # fraction

        if e == 0:
            if f == 0:
                return int(s << 31)
            else:
                while not (f & 0x00000400):
                    f <<= 1
                    e -= 1
                e += 1
                f &= ~0x00000400
                # print s,e,f
        elif e == 31:
            if f == 0:
                return int((s << 31) | 0x7f800000)
            else:
                return int((s << 31) | 0x7f800000 | (f << 13))

        # e = e + (127 -15)
        # f = f << 13
        e += 127 - 15
        f <<= 13

        return int((s << 31) | (e << 23) | f)

    def _hex_to_half_float(self, hf_string):
        try:
            v = struct.unpack(u'H', hf_string.decode(u'hex'))[0]
        except TypeError, e:
            self.logger.error(e)
            self.logger.error(u"Input variable's value is " + hf_string)
            return 0.0

        x = self._half_to_float(v)

        string = struct.pack(u'I', x)
        f = struct.unpack(u'f', string)
        return f[0]

    def _data_reformat(self, hex_string):
        return_str = DEVICES[self.device_code] + u" 00000"
        # return_str = u"LAPIS_RAW0 00000"
        # print type(hex_string)
        # print hex_string

        return_str += u" " + str((self._hex_to_half_float(hex_string[-4:]) / 1024.0) * 9.8)
        return_str += u" " + str((self._hex_to_half_float(hex_string[-8:-4]) / 1024.0) * 9.8)
        return_str += u" " + str((self._hex_to_half_float(hex_string[-12:-8]) / 1024.0) * 9.8)

        # return_str += u" " + str(struct.unpack(u"h", hex_string[-16:-12].decode(u"hex"))[0] / 10.0)
        # return_str += u" " + str(struct.unpack(u"h", hex_string[-20:-16].decode(u"hex"))[0] / 10.0)
        # return_str += u" " + str(struct.unpack(u"h", hex_string[-24:-20].decode(u"hex"))[0] / 10.0)

        return_str += u" " + str(self._hex_to_half_float(hex_string[-16:-12]) / 10.0)
        return_str += u" " + str(self._hex_to_half_float(hex_string[-20:-16]) / 10.0)
        return_str += u" " + str(self._hex_to_half_float(hex_string[-24:-20]) / 10.0)

        # return_str += u" " + str(struct.unpack(u"h", hex_string[-28:-24].decode(u"hex"))[0] / 131.0)
        # return_str += u" " + str(struct.unpack(u"h", hex_string[-32:-28].decode(u"hex"))[0] / 131.0)
        # return_str += u" " + str(struct.unpack(u"h", hex_string[-36:-32].decode(u"hex"))[0] / 131.0)

        return_str += u" " + str(self._hex_to_half_float(hex_string[-28:-24]) / 131.0)
        return_str += u" " + str(self._hex_to_half_float(hex_string[-32:-28]) / 131.0)
        return_str += u" " + str(self._hex_to_half_float(hex_string[-36:-32]) / 131.0)

        return_str += u" " + u"0.0"

        # print return_str
        self.logger.info(return_str)
        return return_str

    def send_cmd(self, cmd):
        self.ser.write((cmd + u"\r").encode(u"utf-8"))

    def receive_data(self):
        rev_data = self.ser.read(self.ser.in_waiting)
        self.logger.info(rev_data[:-2])
        return rev_data

    def run(self):
        self.stop_flag = False
        # time.sleep(5)
        while not self.stop_flag:
            self._data_process()


if __name__ == '__main__':
    pass
    # list_available_ports()
    # send_cmd_seq_modified()

