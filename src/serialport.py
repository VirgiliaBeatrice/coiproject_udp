#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial

COMMAND_DICT = {
    u"CONNECT": u"ATA",
    u"START": u"AT$W0B07=0100",
    u"END": u"AT$W0B07=0000",
    u"DISCONNECT": u"ATH",
}


class SerialPort:

    def __init__(self, port, baudrate=57600):
        self._serial_port = serial.Serial(port, baudrate)
        pass

    def open(self):
        self._serial_port.open()

    def close(self):
        self._serial_port.close()


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
            # print(u"Cannot find {0} device.".format(port))
            pass

    return results


if __name__ == '__main__':
    list_available_ports()
