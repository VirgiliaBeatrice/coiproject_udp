#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import threading

from coiproject_lapissensor.serial_communication import *


COMMAND_DICT = {
    u"CONNECT": u"ATA",
    u"START": u"AT$W0B07=0100",
    u"END": u"AT$W0B07=0000",
    u"DISCONNECT": u"ATH",
}


class MyThread(object):
    def __init__(self):
        self.out_lock = threading.Lock()
        self.threads = []
        self.interrupt_event = threading.Event()

    def main_task(self):
        idx = 0
        while True:
            idx += 1
            t_name = str(idx).decode(u"utf-8")
            self.out_lock.acquire()
            input_str = raw_input(
                u"Generate a new instance? Y/N\r\n").decode(u"utf-8")
            self.out_lock.release()
            if input_str.upper() in u"Y":
                thread = threading.Thread(target=self.sensor_connection,
                                          kwargs={u"t_name": t_name})
                self.threads.append(thread)
                thread.start()
            elif input_str.upper() in u"N":
                self.out_lock.acquire()
                print(u"Keep receive data from until input Ctrl+C to \
                        end process.\r\n")
                self.out_lock.release()
                break
            else:
                self.out_lock.acquire()
                print(u"Invalid input.\r\n")
                self.out_lock.release()
        self.interrupt_event.clear()

        while True:
            try:
                alive_flag = False
                for thread in self.threads:
                    alive_flag = alive_flag or thread.isAlive()
                if not alive_flag:
                    break
            except KeyboardInterrupt:
                self.interrupt_event.set()

    def sensor_connection(self, t_name):
        self.out_lock.acquire()
        print(u"Instance %s has run.\r\n" % t_name)
        list_available_ports()
        input_str = raw_input(u"\r\n"
                              u"Please input port name: ").decode(u'utf-8')
        ser = SerialPort(input_str)
        ser.open()

        def echo_cmd():
            input_string = raw_input(u"\r\n"
                                     u"1. CONNECT\r\n"
                                     u"2. START\r\n"
                                     u"3. END\r\n"
                                     u"4. DISCONNECT\r\n"
                                     u"Please select command from list: "
                                     ).decode(
                u'utf-8')
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
        self.out_lock.release()
        while True:
            try:
                if self.interrupt_event.isSet():
                    raise KeyboardInterrupt
                ser.run_test()
            except KeyboardInterrupt:
                ser.stop_flag = True
                ser.send_cmd(COMMAND_DICT[u"END"])
                time.sleep(3)
                ser.send_cmd(COMMAND_DICT[u"DISCONNECT"])

                time.sleep(3)
                ser.close()
                self.out_lock.acquire()
                print(u"Instance %s has been quited." % t_name)
                self.out_lock.release()
                break


if __name__ == '__main__':
    t = MyThread()
    t.main_task()

