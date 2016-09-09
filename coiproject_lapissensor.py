#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

from coiproject_lapissensor.serial_communication import *


COMMAND_DICT = {
    u"CONNECT": u"ATA",
    u"START": u"AT$W0B07=0100",
    u"END": u"AT$W0B07=0000",
    u"DISCONNECT": u"ATH",
}

# 0xD2FFEBFFF203D6FFCF022BFD4500580029009AC5


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


def send_cmd_seq():
    input_str = raw_input(u"\r\n"
                          u"Please input port name: ").decode(u'utf-8')
    ser = SerialPort(input_str)
    ser.open()

    def echo_cmd():
        input_string = raw_input(
            u"\r\n"
            u"1. CONNECT\r\n"
            u"2. START\r\n"
            u"3. END\r\n"
            u"4. DISCONNECT\r\n"
            u"Please select command from list: ").decode(u'utf-8')
        if input_string in u"1":
            ser.send_cmd(COMMAND_DICT[u"CONNECT"])
        elif input_string in u"2":
            ser.send_cmd(COMMAND_DICT[u"START"])
        elif input_string in u"3":
            ser.send_cmd(COMMAND_DICT[u"END"])
        elif input_string in u"4":
            ser.send_cmd(COMMAND_DICT[u"DISCONNECT"])

    rev_data = None
    while True:
        echo_cmd()
        time.sleep(3)
        try:
            rev_data = ser.receive_data()
        except SerialPortException, e:
            print e
        else:
            break

    print(u"\r\n")
    for line in rev_data[:-1]:
        print(line)
    input_str = raw_input(rev_data[-1]).decode(u'utf-8')
    ser.device_code = rev_data[int(input_str) - 1].split(u" ")[1]
    ser.send_cmd(input_str.encode(u'utf-8'))
    # str.format(input_str)

    # while True:
    #     echo_cmd()
    time.sleep(3)
    try:
        rev_data = ser.receive_data()
    except SerialPortException, e:
        print(e)
    else:
        pass

    for line in rev_data[1:-1]:
        print(line)
    print(u"Press Enter to start.\r\n")
    raw_input()
    ser.send_cmd(COMMAND_DICT[u"START"])
    while True:
        ser.run_test()

    raw_input()
    ser.stop_flag = True
    ser.send_cmd(COMMAND_DICT[u"END"])
    time.sleep(3)
    ser.send_cmd(COMMAND_DICT[u"DISCONNECT"])

    time.sleep(3)
    ser.close()
    print(u"Process has been quited.")
    pass


if __name__ == '__main__':
    list_available_ports()
    # send_cmd_seq_modified()
    send_cmd_seq()
