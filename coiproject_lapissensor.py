#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import serial
import sys
import os

from coiproject_lapissensor.serial_communication import SerialPort


COMMAND_DICT = {
    u"CONNECT": u"ATA",
    u"START": u"AT$W0B07=0100",
    u"END": u"AT$W0B07=0000",
    u"DISCONNECT": u"ATH",
}


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
    currDir = os.path.dirname(os.path.realpath(__file__))
    rootDir = os.path.abspath(os.path.join(currDir, ".."))
    if rootDir not in sys.path:
        sys.path.append(rootDir)
    list_available_ports()
    send_cmd_seq_modified()
