#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Mon Oct  3 18:54:27 2016
##
########################################


import os


class BaseLogFileParser(object):

    def __init__(self, filepath=""):

        self.filepath = filepath
        self.log_file = open(filepath, 'r')
        self.data = {}

    def _cleanup(self):
        """
        Clean's up the data after the parsing has been done.
        """
        self.log_file.close()
        try:
            os.remove(filepath)
        except OSError:
            pass

    def parse_line(self, line):
        """
        Parses a single line of log provided.
        """
        raise NotImplementedError


    def parse(self):
        """
        Parses all the lines of logs in self.log_file
        """
        for line in self.log_file.readlines():
            self.parse_line()

        self._cleanup()
