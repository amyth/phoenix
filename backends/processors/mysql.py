#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 11-05-2017
# @last_modify: Thu May 11 18:07:44 2017
##
########################################

import re

from .core import DataProcessor


class MysqlSentProcessor(DataProcessor):

    def __init__(self, cls):
        self.cls = cls

    def parse_lines(self, lines):
        for line in lines:

            ## Get initial info
            if 'Reply-To' in line:
                parse_reply_to_header(line)

            if 'X-MailerTag' in line:
                parse_mailer_tag_header(line)

            if 'status=' in line:
                parse_status(line)

    def parse_reply_to_header(self, line):
        try:
            message_id = re.findall(self.cls.mid_regex, line)[0]
        except Exception as err:
            print str(err)

    def parse_mailer_tag_header(self, line):
        pass

    def parse_status(self, line):
        pass

