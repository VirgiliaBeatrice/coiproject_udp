#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging


format_dict = {
   1: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
   2: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
   3: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
   4: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
   5: logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
}


class Logger:
    def __init__(self, logname, loglevel, logger):
        # create a logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        # create a handler for writing a log file
        fh = logging.FileHandler(logname)
        fh.setLevel(logging.DEBUG)

        # create a handler for outputting to console
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # define output format of handler
        formatter = format_dict[int(loglevel)]
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Add handler to logger
        # self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def get_log(self):
        return self.logger
