#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Tue Oct  4 14:49:54 2016
##
########################################


import datetime
import os
import re
import subprocess
import uuid

from .core import BaseLogFileParser
from apps.campaigns.documents import Campaign
from apps.messages.documents import Message
from apps.users.documents import User


class MailLogParser(LogFileParser):

    def __init__(self, data_directory="/tmp", primary_tag="X-MailerTag",
            confirm_tag="removed", date_format="%b %d %H:%M:%S",
            *args, **kwargs):
        super(MailLogParser, self).__init__(*args, **kwargs)
        self.uid_blacklist = ['disconnect', 'statistics', 'connect']
        self.data_directory = data_directory
        self.primary_tag = primary_tag
        self.confirm_tag = confirm_tag
        self.primary_data_file = None
        self.sent_data_file = None
        self.date_format = date_format

        #Regular expressions
        self.date_regex = r'\w{3}\s\s\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}'
        self.sender_regex = r'from=<([\w\d@.-_]+)\>'
        self.recipient_regex = r'to=<([\w\d@.-_]+)\>'
        self.mid_regex = r'\w+\/\w+\[[\w\d]+\]\:\s+([\w\d]+)'
        self.campaign_regex = r'[\wd]+-[\w\d]+:\s+([\w\d]+)'

    def _prepare(self):
        """
        Do all the preparation for parsing. Make it easier and quick.
        """

        ## create primary data file
        primary = "%s.log" % uuid.uuid4().__str__()
        primary = os.path.join(self.data_directory, primary)
        subprocess.call(['cat', self.filepath, '|', 'grep', self.primary_tag,
            '>', primary])
        self.primary_data_file = primary

        ## create confirmation data file
        confirm = "%s.log" % uuid.uuid4().__str__()
        confirm = os.path.join(self.data_directory, confirm)
        subprocess.call(['cat', self.filepath, '|', 'grep', self.confirm_tag,
            '>', confirm])
        self.sent_data_file = confirm


    def _confirm_send(self, line):
        try:
            message_id = re.findall(self.mid_regex, line)
            if message_id in self.data:
                self.push_to_mongo(message_id)

        except Exception as err:
            ## Log the error with data
            pass

    def _parse_message_info(self, line):
        data = {}
        try:
            message_id = re.findall(self.mid_regex, line)

            ## double space date fix
            date_fix = re.findall(self.date_regex, line)[0]
            date_fix = datefix.replace("  ", " ")

            data["sent_at"] = date_fix
            data["sender"] = re.findall(self.sender_regex, line)[0]
            data["recipient"] = re.findall(self.recipient_regex, line)[0]
            data["campaign"] = re.findall(self.campaign_regex, line)[0]
            self.data[message_id] = data
        except Exception as err:
            ## Log the error with data
            pass


    def parse_lines(self):
        """
        Parses a single line of log provided.
        """

        with open(self.primary_data_file, 'r') as pd_file:
            for line in pd_file.readlines():
                self._parse_message_info(line)

        with open(self.sent_data_file, 'r') as co_file:
            for line in co_file.readlines():
                self._confirm_send(line)


    def parse(self):
        if self.log_file:
            self._prepare()
            self.parse_lines()


    def push_to_mongo(self, mid):
        data = self.data.get(mid)

        recipient = User.objects.filter(email=data.get('recipient')).first()
        sender = User.objects.filter(email=data.get('sender')).first()
        campaign = Campaign.objects.filter(name=data.get('campaign'))
        sent_at = datetime.datetime.strptime(data.get('sent_at'),
                self.date_format)

        ## create objects if does not exist
        if not recipient:
            recipient = User.objects.create(email=data.get('recipient'))

        if not sender:
            sender = User.objects.create(email=data.get('sender'), utype=2)

        if not campaign:
            campaign = Campaign.objects.create(name=data.get('campaign'))

        message = Message.objects.create(recipient=recipient, sender=sender,
                campaign=campaign, sent_at=sent_at)

        data.pop(mid)



class MailOpenParser(LogFileParser):
    pass
