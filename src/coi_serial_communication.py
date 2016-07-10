#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial
import time
import struct
import loginstance
import threading
import udpclient

COMMAND_DICT = {
    u"CONNECT": u"ATA",
    u"START": u"AT$W0B07=0100",
    u"END": u"AT$W0B07=0000",
    u"DISCONNECT": u"ATH",
}


# TODO(Haoyan.Li): Adjust to current device id.
DEV_0 = u"F5"
DEV_1 = u"E9"
DEV_2 = u"D9"

DEVICES = {
    DEV_0: u"LAPIS_RAW0",
    DEV_1: u"LAPIS_RAW1",
    DEV_2: u"LAPIS_RAW2",
}

logger = loginstance.Logger(
    logname=u"Receive_log.txt",
    loglevel=1,
    logger=u"SerialInfoLog").getlog()


class SerialPort(threading.Thread):

    def __init__(self, port, baudrate=57600):
        super(SerialPort, self).__init__()
        self.ser = serial.Serial(port, baudrate)
        self.udp_client = udpclient.UdpClient()
        self.device_code = u""
        self.stop_flag = True
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
        else:
            logger.info(u"Uncompleted data package has received.")

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
            logger.error(e)
            logger.error(u"Input variable's value is " + hf_string)
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

        return_str += u" " + str(struct.unpack(u"h", hex_string[-16:-12].decode(u"hex"))[0] / 10.0)
        return_str += u" " + str(struct.unpack(u"h", hex_string[-20:-16].decode(u"hex"))[0] / 10.0)
        return_str += u" " + str(struct.unpack(u"h", hex_string[-24:-20].decode(u"hex"))[0] / 10.0)

        return_str += u" " + str(struct.unpack(u"h", hex_string[-28:-24].decode(u"hex"))[0] / 131.0)
        return_str += u" " + str(struct.unpack(u"h", hex_string[-32:-28].decode(u"hex"))[0] / 131.0)
        return_str += u" " + str(struct.unpack(u"h", hex_string[-36:-32].decode(u"hex"))[0] / 131.0)

        # print return_str
        logger.info(return_str)
        return return_str

    def send_cmd(self, cmd):
        self.ser.write((cmd + u"\r").encode(u"utf-8"))

    def receive_data(self):
        rev_data = self.ser.read(self.ser.in_waiting)
        logger.info(rev_data[:-2])
        return rev_data

    def run(self):
        self.stop_flag = False
        # time.sleep(5)
        while not self.stop_flag:
            self._data_process()


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


def send_cmd_seq_modified():
    input_string = raw_input(u"Please input port name: ").encode()
    ser = SerialPort(input_string)
    ser.open()

    ser.send_cmd(COMMAND_DICT[u"CONNECT"])
    time.sleep(3)
    # ser.receive_data()
    ser.device_code = ser.receive_data()[6:8].decode(u"utf-8")
    # logger.info(ser.device_code)

    input_string = raw_input(u"Please input device num: ").encode()
    ser.send_cmd(input_string.format(input_string))
    time.sleep(2)
    ser.receive_data()

    raw_input(u"Press enter key to start.").encode()
    ser.send_cmd(COMMAND_DICT[u"START"])
    ser.start()
    raw_input(u"Press enter key to stop.").encode()
    ser.stop_flag = True
    ser.send_cmd(COMMAND_DICT[u"END"])

    ser.send_cmd(COMMAND_DICT[u"DISCONNECT"])

    ser.close()


if __name__ == '__main__':
    list_available_ports()
    send_cmd_seq_modified()

