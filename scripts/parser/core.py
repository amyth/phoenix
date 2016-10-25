#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Fri Oct  7 14:32:09 2016
##
########################################


import os


class BaseLogFileParser(object):


    def _cleanup(self):
        """
        Clean's up the data after the parsing has been done.
        """
        if hasattr(self, 'log_file'):
            self.log_file.close()
        try:
            #os.remove(self.filepath)
            pass
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
