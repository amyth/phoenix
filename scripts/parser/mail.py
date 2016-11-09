#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Wed Nov  9 15:18:05 2016
##
########################################


import datetime
from multiprocessing.dummy import Pool
import os
import re
import subprocess
import urlparse
import uuid

from mongoengine import Q
from mongoengine.errors import NotUniqueError

from .core import BaseLogFileParser
from apps.campaigns.documents import Campaign
from apps.messages.documents import Message
from apps.users.documents import User, Recruiter


class MailLogParser(BaseLogFileParser):

    def __init__(self, data_directory="/tmp", primary_tag="X-MailerTag",
            confirm_tag="removed", recruiter_tag="X-Uid",
            date_format="%b %d %Y", filepath="", workers=4,
            *args, **kwargs):

        self.data = {}
        self.filepath = filepath
        self.uid_blacklist = ['disconnect', 'statistics', 'connect']
        self.data_directory = data_directory
        self.primary_tag = primary_tag
        self.confirm_tag = confirm_tag
        self.recruiter_tag = recruiter_tag
        self.primary_data_file = None
        self.sent_data_file = None
        self.recruiter_data_file = None
        self.date_format = date_format

        #Regular expressions
        self.date_regex = r'\w{3}\s+\d{1,2}'
        self.sender_regex = r'from=<([\w\d@\.\-\_\/\+]+)\>'
        self.recipient_regex = r'to=<([\w\d@\.\-\_\/\+]+)\>'
        self.mid_regex = r'\w+\/\w+\[[\w\d]+\]\:\s+([\w\d]+)'
        self.campaign_regex = r'[\wd]+-[\w\d]+:\s+([\w\d]+)'
        self.xuid_regex = r'[\wd]+-[\w\d]+:\s+([\w\d\-|]+)'
	self.mongo_list = []
        self.pool = Pool(workers)

        self.log_file = open(self.filepath, 'r')

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
        os.system('cat %s | grep %s > %s' % (
            self.filepath, self.primary_tag, primary
        ))
        self.primary_data_file = primary

        ## create recruiter data file
        recruiter = "%s.log" % uuid.uuid4().__str__()
        recruiter = os.path.join(self.data_directory, recruiter)
        os.system('cat %s | grep %s > %s' % (
            self.filepath, self.recruiter_tag, recruiter
        ))
        self.recruiter_data_file = recruiter

        ## create confirmation data file
        confirm = "%s.log" % uuid.uuid4().__str__()
        confirm = os.path.join(self.data_directory, confirm)
        os.system('cat %s | grep %s > %s' % (
            self.filepath, self.confirm_tag, confirm
        ))
        self.sent_data_file = confirm


    def _confirm_send(self, line):
        try:
            message_id = re.findall(self.mid_regex, line)[0]
            if message_id in self.data:
                self.push_to_mongo(message_id)

        except Exception as err:
            ## Log the error with data
            print line, str(err)

    def _parse_message_info(self, line):
        data = {}
        try:
            message_id = re.findall(self.mid_regex, line)[0]

            ## double space date fix
            date_fix = re.findall(self.date_regex, line)[0]
            date_fix = date_fix.replace("  ", " ")
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
            print line, str(err)

    def _get_recruiter_info(self, line):
	try:
		message_id = re.findall(self.mid_regex, line)[0]
		if message_id in self.data:
		    data = self.data.get(message_id)
		    xuid = re.findall(self.xuid_regex, line)[0]
		    xuid = xuid.split("|")
		    campaign_id = xuid[1]
		    recruiter_id = xuid[-1]
		    data["campaign_id"] = campaign_id
		    data["recruiter_id"] = recruiter_id
		    self.data[message_id] = data
	except Exception as err:
		print line, str(err)


    def parse_lines(self):
        """
        Parses a single line of log provided.
        """

        with open(self.primary_data_file, 'r') as pd_file:
            lines = pd_file.readlines()
            self.pool.map(self._parse_message_info, lines)
            self.pool.close()
            self.pool.join()

        with open(self.recruiter_data_file, 'r') as rec_file:
            lines = rec_file.readlines()
            self.pool.map(self._get_recruiter_info, lines)
            self.pool.close()
            self.pool.join()

        with open(self.sent_data_file, 'r') as co_file:
            lines = co_file.readlines()
            self.pool.map(self._confirm_send, lines)
            self.pool.close()
            self.pool.join()

    def parse(self):
        if self.log_file:
            self._prepare()
            self.parse_lines()
	    self._insert()
            self._cleanup()

    def _insert(self):
	Message.objects.insert(self.mongo_list)

    def push_to_mongo(self, mid):

        campaign = None
        recruiter = None
        data = self.data.get(mid)
        recipient = User.objects.filter(email=data.get('recipient')).first()
        sent_at = datetime.datetime.strptime(data.get('sent_at'),
                self.date_format)

        ## create objects if does not exist
        if not recipient:
            recipient = User.objects.create(email=data.get('recipient'))


        if ('recruiter_id' in data) or ('sender' in data):
            recruiter_id = data.get('recruiter_id')
	    sender = data.get('sender')
            recruiter = Recruiter.objects(Q(uid=recruiter_id) | Q(email=sender)).first()
            if not recruiter:
                recruiter = Recruiter.objects.create(uid=recruiter_id, email=sender)

	try:
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
	except NotUniqueError:
		campaign = Campaign.objects.get(name=data.get('campaign'))

        message = Message(recipient=recipient, sender=recruiter,
                campaign=campaign, sent_at=sent_at)

        self.data.pop(mid)
	self.mongo_list.append(message)


class OpenLogParser(BaseLogFileParser):

    def __init__(self, filepath, data_directory="/tmp", date_format="%d/%b/%Y",
            workers=4, *args, **kwargs):

        self.filepath = filepath
        self.data = []
        self.date_format = date_format

        #Regular expressions
        self.date_regex = r'[\d]+\/[\w]+\/[\d]+'
        self.qs_regex = r'/media/images/dot.gif\?([\w\d=&.@]+)'

        self.log_file = open(self.filepath, 'r')
        self.pool = Pool(workers)

    def parse(self):
        if self.log_file:
            self.parse_lines()
            self._cleanup()

    def parse_lines(self):
        """
        Parses a single line of log provided.
        """

        lines = self.log_file.readlines()
        self.pool.map(self._parse_message_info, lines)
        self.pool.close()
        self.pool.join()

        self.pool.map(self.update_open_status, self.data)
        self.pool.close()
        self.pool.join()

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

    def update_open_status(self, obj):
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
            message.opened = True
            message.opened_at = datetime.datetime.strptime(
                    obj.get('open_date'), self.date_format)
            message.save()



class ClickLogParser(BaseLogFileParser):

    def __init__(self, filepath, data_directory="/tmp", date_format="%d/%b/%Y",
            primary_tag="etm_content.*utm_camp|utm_camp.*etmcontent",
            workers=4, *args, **kwargs):

        self.filepath = filepath
        self.data = []
        self.date_format = date_format
        self.primary_data_file = None
        self.primary_tag = primary_tag
        self.data_directory = data_directory

        #Regular expressions
        self.date_regex = r'\w{3}\s+\d{1,2}'
        self.qs_regex = r'[\?]([\w\d\=\&\/\-\_\.\%\:\+\?]+)'

        self.log_file = open(self.filepath, 'r')
        self.pool = Pool(workers)

    def _cleanup(self):
        super(ClickLogParser, self)._cleanup()
        try:
            pass
            #os.remove(self.primary_data_file)
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
            lines = pd_file.readlines()
            self.pool.map(self._parse_message_info, lines)
            self.pool.close()
            self.pool.join()

        self.pool.map(self.update_click_status, self.data)
        self.pool.close()
        self.pool.join()

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

    def update_click_status(self, obj):

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
            message.clicked = True
            message.clicked_at = datetime.datetime.strptime(
                    obj.get('click_date'), self.date_format)
            message.save()
