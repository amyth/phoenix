#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Thu Oct  6 10:36:46 2016
##
########################################


import datetime
import os
import re
import subprocess
import urlparse
import uuid

from .core import BaseLogFileParser
from apps.campaigns.documents import Campaign
from apps.messages.documents import Message
from apps.users.documents import User


class MailLogParser(LogFileParser):

    def __init__(self, data_directory="/tmp", primary_tag="X-MailerTag",
            confirm_tag="removed", recruiter_tag="X-Uid",
            date_format="%b %d %Y",
            *args, **kwargs):
        super(MailLogParser, self).__init__(*args, **kwargs)
        self.uid_blacklist = ['disconnect', 'statistics', 'connect']
        self.data_directory = data_directory
        self.primary_tag = primary_tag
        self.confirm_tag = confirm_tag
        self.primary_data_file = None
        self.sent_data_file = None
        self.recruiter_data_file = None
        self.date_format = date_format

        #Regular expressions
        self.date_regex = r'\w{3}\s+\d{1,2}'
        self.sender_regex = r'from=<([\w\d@.-_]+)\>'
        self.recipient_regex = r'to=<([\w\d@.-_]+)\>'
        self.mid_regex = r'\w+\/\w+\[[\w\d]+\]\:\s+([\w\d]+)'
        self.campaign_regex = r'[\wd]+-[\w\d]+:\s+([\w\d]+)'
        self.xuid_regex = r'[\wd]+-[\w\d]+:\s+([\w\d\-|]+)'

    def _cleanup(self):
        super(MailLogParser, self)._cleanup()
        for fobj in [self.primary_data_file, self.sent_data_file,
                self.recruiter_data_file]:
            try:
                os.remove(fobj)
            except OSError:
                pass

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

        ## create recruiter data file
        recruiter = "%s.log" % uuid.uuid4().__str__()
        recruiter = os.path.join(self.data_directory, recruiter)
        subprocess.call(['cat', self.filepath, '|', 'grep', self.recruiter_tag,
            '>', recruiter])
        self.recruiter_data_file = recruiter

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
            date_fix = "%s %d" % (date_fix, datetime.datetime.now().year)

            ## sender fix
            sender = re.findall(self.sender_regex, line)
            sender = sender[0] if sender else None

            data["sent_at"] = date_fix
            data["sender"] = sender
            data["recipient"] = re.findall(self.recipient_regex, line)[0]
            data["campaign"] = re.findall(self.campaign_regex, line)[0]
            self.data[message_id] = data
        except Exception as err:
            ## Log the error with data
            pass

    def _get_recruiter_info(self, line):
        message_id = re.findall(self.mid_regex, line)
        if message_id in self.data:
            data = self.data.get(message_id)
            xuid = re.findall(self.xui_regex, line)
            xuid = xuid.split("|")
            campaign_id = xuid[1]
            recruiter_id = xuid[-1]
            data["campaign_id"] = campaign_id
            data["recruiter_id"] = recruiter_id
            self.data[mid] = data


    def parse_lines(self):
        """
        Parses a single line of log provided.
        """

        with open(self.primary_data_file, 'r') as pd_file:
            for line in pd_file.readlines():
                self._parse_message_info(line)

        with open(self.recruiter_data_file, 'r') as rec_file:
            for line in rec_file.readlines():
                self._get_recruiter_info(line)

        with open(self.sent_data_file, 'r') as co_file:
            for line in co_file.readlines():
                self._confirm_send(line)


    def parse(self):
        if self.log_file:
            self._prepare()
            self.parse_lines()
            self._cleanup()


    def push_to_mongo(self, mid):

        campaign = None
        data = self.data.get(mid)
        recipient = User.objects.filter(email=data.get('recipient')).first()
        sent_at = datetime.datetime.strptime(data.get('sent_at'),
                self.date_format)

        ## create objects if does not exist
        if not recipient:
            recipient = User.objects.create(email=data.get('recipient'))


        if 'recruiter_id' in data:
            recruiter_id = data.get('recruiter_id')
            recruiter = Recruiter.objects.filter(uid=recruiter_id).first()
            if not recruiter:
                recruiter = Recruiter.objects.create(uid=recruiter_id)

        if 'campaign_id' in data:
            campaign = Campaign.objects.filter(name=data.get('campaign'),
                    cid=data.get('campaign_id')).first()
            if not campaign:
                campaign = Campaign.objects.create(name=data.get('campaign'),
                        cid=data.get('campaign_id'))
        else:
            campaign = Campaign.objects.filter(name=data.get('campaign')).first()
            if not campaign:
                campaign = Campaign.objects.create(name=data.get('campaign'))

        message = Message.objects.create(recipient=recipient, sender=recruiter,
                campaign=campaign, sent_at=sent_at)

        dat.pop(mid)


class OpenLogParser(LogFileParser):

    def __init__(self, data_directory="/tmp", date_format="%d/%b/%Y",
            *args, **kwargs):
        super(OpenLogParser, self).__init__(*args, **kwargs)

        self.data = []
        self.date_format = date_format

        #Regular expressions
        self.date_regex = r'[\d]+\/[\w]+\/[\d]+'
        self.qs_regex = r'/media/images/dot.gif\?([\w\d=&.@]+)'


    def parse(self):
        if self.log_file:
            self.parse_lines()
            self._cleanup()

    def parse_lines(self):
        """
        Parses a single line of log provided.
        """

        for line in self.log_file.readlines():
            self._parse_message_info(line)

        self.update_open_status()

    def get_normalized_email(email):
        if '@' in email:
            return email
        return self.decrypt(email.replace(" ", "+"))

    def get_normalized_campaign(self, camp):
        if camp.startswith('sendJob'):
            return 'sendJob'
        return camp

    def get_normalized_cdate(self, cdate):
        return datetime.datetime.strptime(cdate, '%Y%m%d')

    def _parse_message_info(self, line):
        try:
            data = {}
            open_date = re.findall(self.date_regex, line)[0]
            qs_string = re.findall(self.qs_regex, line)[0]
            qs = urlparse.parse_qs(qs_string)
            data['open_date'] = open_date
            data['email'] = self.get_normalized_email(qs.get('user_email')[0])
            data['campaign'] = self.get_normalized_campaign(qs.get('utm_camp')[0])
            data['cdate'] = self.get_normalized_cdate(qs.get('utm_campdt')[0])

            if 'tid' in qs:
                tid = urllib.unquote(qs.get('tid')).split('|')
                data['campaign_id'] = tid[1]
            self.data.append(data)
        except Exception as err:
            ## Log the error with data
            pass

    def update_open_status(self):
        for obj in self.data:

            if 'campaign_id' in obj:
                campaign = Campaign.objects.filter(name=obj.get('campaign'),
                        cid=obj.get('campaign_id')).first()
            else:
                campaign = Campaign.objects.filter(name=obj.get('campaign')).first()

            cdate = obj.get('cdate')
            email = obj.get('email')

            user = User.objects.filter(email=email).first()
            message = Message.objects.filter(campaign=campaign, recipient=user,
                    sent_at=cdate)
            if message:
                message.opened_at = datetime.datetime.strptime(
                        obj.get('open_date'), self.date_format)
                message.save()



class ClickLogParser(LogFileParser):

    def __init__(self, data_directory="/tmp", date_format="%d/%b/%Y",
            primary_tag="etm_content.*utm_camp|utm_camp.*etmcontent",
            *args, **kwargs):
        super(OpenLogParser, self).__init__(*args, **kwargs)

        self.data = []
        self.date_format = date_format
        self.primary_data_file = None
        self.primary_tag = primary_tag

        #Regular expressions
        self.date_regex = r'\w{3}\s+\d{1,2}'
        self.qs_regex = r'[\?]([\w\d\=\&\/\-\_\.\%\:\+\?]+)'


    def _cleanup(self):
        super(ClickLogParser, self)._cleanup()
            try:
                os.remove(self.primary_data_file)
            except OSError:
                pass

    def _prepare(self):
        ## create primary data file
        primary = "%s.log" % uuid.uuid4().__str__()
        primary = os.path.join(self.data_directory, primary)
        subprocess.call(['cat', self.filepath, '|', 'grep', '-E',
            self.primary_tag, '>', primary])
        self.primary_data_file = primary


    def parse(self):
        if self.log_file:
            self._prepare()
            self.parse_lines()
            self._cleanup()

    def parse_lines(self):
        """
        Parses a single line of log provided.
        """

        with open(self.primary_data_file, 'r') as pd_file:
            for line in pd_file.readlines():
                self._parse_message_info(line)

        self.update_click_status()


    def get_normalized_email(self, cont):
        cont = cont.split("|")
        email = cont[3]
        if '@' in email:
            return email
        return self.decrypt(email.replace(" ", "+"))

    def get_normalized_campaign(self, camp):
        if camp.startswith('sendJob'):
            return 'sendJob'
        return camp

    def get_normalized_cdate(self, cont):
        cont = cont.split("|")
        cdate = cont[2]
        cdate = re.findall(r'[\d]{4}\-[\d]{1,2}\-[\d]{1,2}', cdate)

        return datetime.datetime.strptime(cdate, '%Y-%m-%d')

    def _parse_message_info(self, line):
        data = {}
        try:
            date_fix = re.findall(self.date_regex, line)[0]
            date_fix = datefix.replace("  ", " ")
            date_fix = "%s %d" % (date_fix, datetime.datetime.now().year)

            qs_string = re.findall(self.qs_regex, line)[0]
            qs = urlparse.parse_qs(qs_string)
            data['click_date'] = date_fix
            data['email'] = self.get_normalized_email(qs.get('etm_content')[0])
            data['campaign'] = self.get_normalized_campaign(qs.get('utm_camp')[0])
            data['cdate'] = self.get_normalized_cdate(qs.get('etm_content')[0])

            if 'tid' in qs:
                tid = urllib.unquote(qs.get('tid')).split('|')
                data['campaign_id'] = tid[1]
            self.data.append(data)
        except Exception as err:
            ## Log the error with data
            pass

    def update_click_status(self):

        for obj in self.data:
            if 'campaign_id' in obj:
                campaign = Campaign.objects.filter(name=obj.get('campaign'),
                        cid=obj.get('campaign_id')).first()
            else:
                campaign = Campaign.objects.filter(name=obj.get('campaign')).first()

            cdate = obj.get('cdate')
            email = obj.get('email')

            user = User.objects.filter(email=email).first()
            message = Message.objects.filter(campaign=campaign, recipient=user,
                    sent_at=cdate)
            if message:
                message.clicked_at = datetime.datetime.strptime(
                        obj.get('click_date'), self.date_format)
                message.save()
