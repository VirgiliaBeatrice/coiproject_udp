#!/usr/bin/python
# -*- coding: utf-8 -*-


import random
import time
# import threading

from collections import deque

import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Plotter:
    def __init__(self):
        self.max_length = 100
        self.ring_buffer = deque(maxlen=self.max_length)
        # self.th = threading.Thread(target=self._generate_data)
        # self.th.start()

        self.fig = plt.figure()
        self.ax = plt.axes()
        # self.lines_data = {}
        self.interval = 2000

        self.line, = self.ax.plot([])

        self.ani = animation.FuncAnimation(
            self.fig,
            self._update_line,
            fargs=(self.fig, self.ax, self.line, self.ring_buffer),
            interval=self.interval
        )
        # plt.ion()
        plt.show()

    def append(self, iter_item):
        self.ring_buffer.append(iter_item)
        
    # def add_line(self, line_name):
    #     self.lines[line_name], = self.ax.plot([])

    @staticmethod
    def _update_line(framenumber, *args):
        ax = args[1]
        line = args[2]
        y_array = list(args[3])
        x_array = [idx for idx in range(len(y_array))]

        if y_array:
            line.set_ydata(y_array)
            line.set_xdata(x_array)
            ax.set_ylim([-10, 10])
            ax.set_xlim([x_array[0], x_array[-1]])

        return line,

    def _generate_data(self):
        while True:
            self.ring_buffer.append(random.randint(-10, 10))
            # print(self.ring_buffer)
            time.sleep(0.05)

    # def start(self):
    #     plt.show()


if __name__ == '__main__':
    plotter = Plotter()
    pass
