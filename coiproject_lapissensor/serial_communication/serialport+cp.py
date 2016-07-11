#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial
import time
import struct


COMMAND_DICT = {
    u"CONNECT": u"ATA",
    u"START": u"AT$W0B07=0100",
    u"END": u"AT$W0B07=0000",
    u"DISCONNECT": u"ATH",
}


class SerialPort:

    def __init__(self, port, baudrate=57600):
        self.serial_port = serial.Serial(port, baudrate)
        self.serial_port.reset_input_buffer()

    def open(self):
        try:
            self.serial_port.open()
        except (OSError, serial.SerialException):
            self.serial_port.close()
            self.serial_port.open()

    def close(self):
        time.sleep(1)
        self.serial_port.close()

    def _data_process(self):
        pass

    def send_cmd(self, cmd):
        self.serial_port.write((cmd + u"\r").encode(u"utf-8"))


def check_rev_buffer(ser):
    print "check buffer"
    while 1:
        curr_line = ser.readline()
        print curr_line


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


def half_to_float(h):
    s = int((h >> 15) & 0x00000001)     # sign
    e = int((h >> 10) & 0x0000001f)     # exponent
    f = int(h &         0x000003ff)     # fraction

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

    e = e + (127 -15)
    f = f << 13

    return int((s << 31) | (e << 23) | f)


def hex_to_half_float(hf_string):
    # print hf_string
    v = struct.unpack(u'H', hf_string.decode(u'hex'))[0]
    x = half_to_float(v)

    str = struct.pack(u'I', x)
    f = struct.unpack(u'f', str)
    return f[0]


def send_cmd_seq():
    input_string = raw_input(u"Please input port name: ").encode()
    ser = SerialPort(input_string)
    ser.open()

    ser.send_cmd(COMMAND_DICT[u"CONNECT"])
    time.sleep(3)
    echo_string = ser.serial_port.read(ser.serial_port.in_waiting)
    print echo_string

    input_string = raw_input().encode()
    ser.send_cmd(input_string.format(input_string))
    time.sleep(2)
    echo_string = ser.serial_port.read(ser.serial_port.in_waiting)
    print echo_string

    raw_input(u"Waiting to start.").encode()
    ser.send_cmd(COMMAND_DICT[u"START"])

    while 1:
        echo_string = ser.serial_port.readline()
        pos = echo_string.find(u"VALUE:")
        if pos != -1:
            # print echo_string[(pos + 6):(pos + 48)]
            data_process(echo_string[(pos + 6):(pos + 48)])

        # print echo_string

    input_string = raw_input(u"Waiting to stop.").encode()
    ser.send_cmd(COMMAND_DICT[u"END"])
    ser.send_cmd(COMMAND_DICT[u"DISCONNECT"])


def data_process(hex_string):
    return_str = u"LAPIS_RAW0 00000"
    # print type(hex_string)
    # print hex_string

    return_str += u" " + str((hex_to_half_float(hex_string[-4:]) / 1024.0) * 9.8)
    return_str += u" " + str((hex_to_half_float(hex_string[-8:-4]) / 1024.0) * 9.8)
    return_str += u" " + str((hex_to_half_float(hex_string[-12:-8]) / 1024.0) * 9.8)

    return_str += u" " + str(struct.unpack(u"h", hex_string[-16:-12].decode(u"hex"))[0] / 10.0)
    return_str += u" " + str(struct.unpack(u"h", hex_string[-20:-16].decode(u"hex"))[0] / 10.0)
    return_str += u" " + str(struct.unpack(u"h", hex_string[-24:-20].decode(u"hex"))[0] / 10.0)

    return_str += u" " + str(struct.unpack(u"h", hex_string[-28:-24].decode(u"hex"))[0] / 131.0)
    return_str += u" " + str(struct.unpack(u"h", hex_string[-32:-28].decode(u"hex"))[0] / 131.0)
    return_str += u" " + str(struct.unpack(u"h", hex_string[-36:-32].decode(u"hex"))[0] / 131.0)

    print return_str
    return return_str

# 0x78FF1200DA0374FECBFFA9FD96FFC6FFE8F66C5F
# serial.serial_for_url()

if __name__ == '__main__':
    list_available_ports()
    send_cmd_seq()
    # data_process(u"0x78FF1200DA0374FECBFFA9FD96FFC6FFE8F66C5F")
