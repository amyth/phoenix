#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Thu May 11 14:09:48 2017
##
########################################


import datetime
from multiprocessing.dummy import Pool
import os
import re
import subprocess
import time
import urlparse
import urllib
import uuid

from mongoengine import Q
from mongoengine.errors import NotUniqueError

from .core import BaseLogFileParser
from apps.messages.documents import RecruiterMessages
from backends.mongo import MongoBackend
from backends.mysql import MySQLMergeBackend


class MailLogParser(BaseLogFileParser):

    def __init__(self, data_directory="/tmp", primary_tag="X-MailerTag",
            confirm_tag="removed", recruiter_tag="X-Uid", reply_tag="Reply-To",
            date_format="%b %d %Y", filepath="", workers=8, checkpoint=10000,
            insert_backends=[MongoBackend], *args, **kwargs):

        self.data = {}
        self.filepath = filepath
        self.uid_blacklist = ['disconnect', 'statistics', 'connect']
        self.data_directory = data_directory
        self.primary_tag = primary_tag
        self.confirm_tag = confirm_tag
        self.recruiter_tag = recruiter_tag
        self.reply_tag = reply_tag
        self.primary_data_file = None
        self.sent_data_file = None
        self.recruiter_data_file = None
        self.date_format = date_format
	self.checkpoint = checkpoint
	self.inserting = False
        self.insert_backends = [backend() for backend in insert_backends]

        #Regular expressions
        self.date_regex = r'\w{3}\s+\d{1,2}'
        self.sender_regex = r'from=<([\w\d@\.\-\_\/\+]+)\>'
        self.recipient_regex = r'to=<([\w\d@\.\-\_\/\+]+)\>'
        self.mid_regex = r'\w+\/\w+\[[\w\d]+\]\:\s+([\w\d]+)'
        self.campaign_regex = r'[\wd]+-[\w\d]+:\s+([\w\d]+)'
        self.xuid_regex = r'[\wd]+-[\w\d]+:\s+([\w\d\-|\~\!\@\#\$\%\^\&\*\(\)\+\=\{\}\[\]\\\'\"\:\;\?\/\>\<\.\,\`]+)'
        self.reply_to_regex = r'Reply-To: ([\w\d@\.\-\_\/\+]+)'
	self.sf_data = {}
        self.final_data = []
        self.workers = workers
	self.pcount = 0

        self.log_file = open(self.filepath, 'r')

	#Debug information
	self.mailer_tag_log = open('/tmp/mailer_tag_log.txt', 'w')
	self.recruiter_log = open('/tmp/recruiter_log.txt', 'w')
	self.confirm_log = open('/tmp/confirm_log.txt', 'w')

    def _confirm_send(self, line):
        try:
            message_id = re.findall(self.mid_regex, line)[0]
            if message_id in self.data:
                data = self.data.get(message_id)
                data["delivered"] = True
                self.data[message_id] = data
                self.push_data(message_id)
        except Exception as err:
            print line, str(err)
            #TODO: Implement logging and log the lines that throw an exception
	    self.confirm_log.writelines(['%s, %s\n' % (line, err)])

    def _parse_message_info(self, line):
        data = {}
        try:
            message_id = re.findall(self.mid_regex, line)[0]

            ## double space date fix
            date_fix = re.findall(self.date_regex, line)[0]
            date_fix = date_fix.replace("  ", " ")
	    year = datetime.datetime.now().year
	    year = year - 1 if date_fix == "Dec 31" else year
            date_fix = "%s %d" % (date_fix, year)

            ## sender fix
            sender = re.findall(self.sender_regex, line)
            sender = sender[0] if sender else None

            data["sent_at"] = date_fix
            data["sender"] = sender
            data["recipient"] = re.findall(self.recipient_regex, line)[0]
            data["campaign"] = self.get_normalized_campaign(
		    re.findall(self.campaign_regex, line)[0])
            self.data[message_id] = data
	    self.pcount += 1
	    print "%d" % self.pcount
	    if data["campaign"] == "sendJob":
		self.mailer_tag_log.writelines(['%s\n' % message_id])
        except Exception as err:
            ## Log the error with data
            print line, str(err)
	    self.mailer_tag_log.writelines(['%s %s\n' % (line, str(err))])

    def _get_recruiter_info(self, line):
	try:
            message_id = re.findall(self.mid_regex, line)[0]
            if message_id in self.data:
                data = self.data.get(message_id)
                xuid = re.findall(self.xuid_regex, line)[0]
                xuid = xuid.split("|")
                campaign_id = self.get_campaign_id(xuid)
                recruiter_id = xuid[-1]
                data["campaign_id"] = campaign_id
                data["recruiter_id"] = recruiter_id
                self.data[message_id] = data
		if xuid[0].startswith("sendJob"):
    		    self.recruiter_log.writelines(['%s\n' % message_id])
	except Exception as err:
            print line, str(err)
	    self.recruiter_log.writelines(['%s %s\n' % (line, str(err))])


    def parse_lines(self):
        """
        Parses a single line of log provided.
        """

	print "Parsing Data ..."
	lines = self.log_file.readlines()
    	for line in lines:
	    if self.primary_tag in line:
	    	self._parse_message_info(line)
	    if self.recruiter_tag in line:
	    	self._get_recruiter_info(line)
 	    if self.confirm_tag in line:
	    	self._confirm_send(line)

    def parse(self):
        if self.log_file:
            self.parse_lines()
	    self._insert()
            self._cleanup()
	return None

    def _insert(self):

        for backend in self.insert_backends:
            backend.insert_sents(self.sf_data)

	self.sf_data.clear()
	del self.sf_data
        return None

    def push_data(self, mid):

        data = self.data.get(mid)
        date = data.get('sent_at')
        campaign = data.get('campaign', 'nocampaign')
        campaign_id = data.get('campaign_id', 'nocampaignid')
        recruiter_id = data.get('recruiter_id', 'norecruiterid')

        date_data = self.sf_data.get(date, {})
        camp_data = date_data.get(campaign, {})
        reid_data = camp_data.get(recruiter_id, {})
        caid_data = reid_data.get(campaign_id, {})
        caid_data['sent'] = caid_data.get('sent', 0) + 1
        reid_data[campaign_id] = caid_data
        camp_data[recruiter_id] = reid_data
        date_data[campaign] = camp_data
        self.sf_data[date] = date_data

	if campaign == "sendJob":
	    self.confirm_log.writelines(['%s\n' % mid])

        del self.data[mid]


class OpenLogParser(BaseLogFileParser):

    def __init__(self, filepath, data_directory="/tmp", date_format="%d/%b/%Y",
            workers=4, insert_backends=[MongoBackend],
            *args, **kwargs):

        self.filepath = filepath
        self.data = {}
        self.date_format = date_format

        #Regular expressions
        self.action_time_regex = r'(\d{0,2}\/\w{3,3}\/\d+\:\d+\:\d+\:\d+)'
        self.date_regex = r'[\d]+\/[\w]+\/[\d]+'
        self.qs_regex = r'/media/images/dot.gif\?([\w\d=&.@\/\_\-\+\|\%\:]+)'
	self.uemail_regex = r'user_email=([\w\d\+\_\/\=\\\-]+)'

        self.log_file = open(self.filepath, 'r')
	todays_date = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%d_%b_%Y')
	self.open_data_file = open('/tmp/%s_open_data.log' % todays_date, 'w')
        self.workers = workers
        self.insert_backends = [backend() for backend in insert_backends]

    def parse(self):
        if self.log_file:
            self.parse_lines()
            self._cleanup()

    def parse_lines(self):
        """
        Parses a single line of log provided.
        """

        lines = self.log_file.readlines()
        self.total = len(lines)
        self.prog = 0
        for line in lines:
            self._parse_message_info(line)

        self.update_open_status()

    def get_normalized_email(self, email):
        if '@' in email:
            return email
        return self.decrypt_aes(email.replace(" ", "+"))

    def get_normalized_cdate(self, cdate):
        return datetime.datetime.strptime(cdate, '%Y%m%d').strftime('%b %d %Y')

    def _parse_message_info(self, line):
        try:
            data = {}
            qs_string = re.findall(self.qs_regex, line)[0]
            qs = urlparse.parse_qs(qs_string)
            cdate = self.get_normalized_cdate(qs.get('utm_campdt')[0])
            campaign = self.get_normalized_campaign(qs.get('utm_camp')[0])
            user_email = re.findall(self.uemail_regex, line)[0]
            campaign_id = 'nocampaignid'
            recruiter_id = 'norecruiterid'

            if 'tid' in qs:
                tid = urllib.unquote(qs.get('tid')[0]).split('|')
                campaign_id = self.get_campaign_id(tid)
                recruiter_id = tid[-1]

            date_data = self.data.get(cdate, {})
            camp_data = date_data.get(campaign, {})
            recr_data = camp_data.get(recruiter_id, {})
            caid_data = recr_data.get(campaign_id, {})

            caid_data['opened'] = caid_data.get('opened', 0) + 1
            recr_data[campaign_id] = caid_data
            camp_data[recruiter_id] = recr_data
            date_data[campaign] = camp_data

            ac_time = re.findall(self.action_time_regex, line)
            ac_time = ac_time[0] if ac_time else ""

            self.data[cdate] = date_data
            self.open_data_file.writelines(['%s %s %s %s %s (%s)\n' % (cdate, campaign,
                    self.get_normalized_email(user_email), campaign_id, recruiter_id, ac_time)])
            self.prog += 1
            print "%s/%s" % (self.prog, self.total)
        except Exception as err:
            ## Log the error with data
            print line, str(err)
            #raise

    def update_open_status(self):
        for backend in self.insert_backends:
            backend.insert_opens(self.data)

	self.data.clear()
        del self.data
        return None


class ClickLogParser(BaseLogFileParser):

    def __init__(self, filepath, data_directory="/tmp", date_format="%d/%b/%Y",
            primary_tag="etm_content", insert_backends=[MongoBackend],
            workers=4, *args, **kwargs):

        self.filepath = filepath
        self.data = {}
        self.date_format = date_format
        self.primary_data_file = None
        self.primary_tag = primary_tag
        self.data_directory = data_directory

        #Regular expressions
        self.action_time_regex = r'^(\w{3,3}\s{0,2}\d{0,2}\s\d+\:\d+\:\d+)'
        self.date_regex = r'\w{3}\s+\d{1,2}'
        self.qs_regex = r'[\?]([\w\d\=\&\/\-\_\.\%\:\+\?\|\@]+)'
        self.pa_string = 'primaryAction'
        self.job_url_regex = r'myshine/jobs/[(\w\d\-\_\\\/)]+'
        self.pa_string = 'primaryAction'

        if 'ClickLogParser' in str(self.__class__):
            todays_date = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%d_%b_%Y')
            self.click_data_file = open('/tmp/%s_click_data.log' % todays_date, 'w')

        self.log_file = open(self.filepath, 'r')
        self.workers = workers
        self.insert_backends = [backend() for backend in insert_backends]

    def _cleanup(self):
        super(ClickLogParser, self)._cleanup()
        try:
            pass
            os.remove(self.primary_data_file)
        except OSError:
            pass

    def _prepare(self):
        ## create primary data file
        primary = "%s.log" % uuid.uuid4().__str__()
        primary = os.path.join(self.data_directory, primary)
        os.system('cat %s | grep %s | grep utm_campaign| grep -v "myshine/login" | grep -v "appParams" > %s' % (
            self.filepath, self.primary_tag, primary
        ))
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
            self.total = len(lines)
            self.prog = 0
            self.errors = 0
            for line in lines:
                self._parse_message_info(line)

        self.update_click_status()

    def get_normalized_email(self, cont):
        cont = cont.split("|")
        email = cont[3]
        if '@' in email:
            return email
        return self.decrypt_aes(email.replace(' ', '+'))

    def get_normalized_cdate(self, cont):
        cont = cont.split("|")
        cdate = cont[2]
        cdate = re.findall(r'[\d]{4}\-[\d]{1,2}\-[\d]{1,2}', cdate)[0]
        return datetime.datetime.strptime(cdate, '%Y-%m-%d').strftime('%b %d %Y')

    def _parse_message_info(self, line):
        data = {}
        try:
            qs_string = re.findall(self.qs_regex, line)
	    qs_string = [x for x in qs_string if self.primary_tag in x][0]
            qs = urlparse.parse_qs(urllib.unquote(qs_string))
            campaign = self.get_normalized_campaign(qs.get('utm_campaign')[0])
            cdate = self.get_normalized_cdate(qs.get('etm_content')[0])
	    user_email = self.get_normalized_email(qs.get('etm_content')[0])
            campaign_id = 'nocampaignid'
            recruiter_id = 'norecruiterid'

            if 'tid' in qs:
                tid = urllib.unquote(qs.get('tid')[0]).split('|')
                campaign_id = self.get_campaign_id(tid)
                recruiter_id = tid[-1]

            data['campaign_id'] = campaign_id
            data['recruiter_id'] = recruiter_id

            date_data = self.data.get(cdate, {})
            camp_data = date_data.get(campaign, {})
            recr_data = camp_data.get(recruiter_id, {})
            caid_data = recr_data.get(campaign_id, {})

            caid_data['clicked'] = caid_data.get('clicked', 0) + 1

            if self.pa_string in line:
                caid_data['primary_action'] = 1

            recr_data[campaign_id] = caid_data
            camp_data[recruiter_id] = recr_data
            date_data[campaign] = camp_data

            self.data[cdate] = date_data
            self.prog += 1


            ac_time = re.findall(self.action_time_regex, line)
            ac_time = ac_time[0] if ac_time else ""

            ## Add job id to click log file
            job_id = ""
            if 'myshine/jobs' in line:
                job_url = re.findall(self.job_url_regex, line)
                if len(job_url):
                    job_id = re.findall(r'[(\d)]+', job_url)
                    job_id = job_id[0] if job_id else ""

	    self.click_data_file.writelines(['%s %s %s %s %s %s (%s)\n' % (cdate, campaign,
		    user_email, campaign_id, recruiter_id, job_id, ac_time)])

            print "%s/%s" % (self.prog, self.total)
        except Exception as err:
            ## Log the error with data
            print line, str(err)
            self.errors += 1

    def update_click_status(self):
        for backend in self.insert_backends:
            backend.insert_clicks(self.data)

	self.data.clear()
        del self.data
        return None
