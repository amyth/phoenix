#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Wed Nov 16 17:05:28 2016
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


class MailLogParser(BaseLogFileParser):

    def __init__(self, data_directory="/tmp", primary_tag="X-MailerTag",
            confirm_tag="removed", recruiter_tag="X-Uid", reply_tag="Reply-To",
            date_format="%b %d %Y", filepath="", workers=8, checkpoint=10000,
            *args, **kwargs):

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

        #Regular expressions
        self.date_regex = r'\w{3}\s+\d{1,2}'
        self.sender_regex = r'from=<([\w\d@\.\-\_\/\+]+)\>'
        self.recipient_regex = r'to=<([\w\d@\.\-\_\/\+]+)\>'
        self.mid_regex = r'\w+\/\w+\[[\w\d]+\]\:\s+([\w\d]+)'
        self.campaign_regex = r'[\wd]+-[\w\d]+:\s+([\w\d]+)'
        self.xuid_regex = r'[\wd]+-[\w\d]+:\s+([\w\d\-|]+)'
        self.reply_to_regex = r'Reply-To: ([\w\d@\.\-\_\/\+]+)'
	self.mongo_data = {}
        self.final_data = []
        self.workers = workers
	self.ptotal = 0
	self.pcount = 0

        self.log_file = open(self.filepath, 'r')

	#Debug information
	self.mailer_tag_log = open('/tmp/mailer_tag_log.txt', 'w')
	self.recruiter_log = open('/tmp/recruiter_log.txt', 'w')
	self.confirm_log = open('/tmp/confirm_log.txt', 'w')

    def _cleanup(self):
        super(MailLogParser, self)._cleanup()
        #for fobj in [self.primary_data_file, self.sent_data_file,
        #        self.recruiter_data_file]:
        #    try:
        #        os.remove(fobj)
        #    except OSError:
        #        pass
	pass

    def _prepare(self):
        """
        Do all the preparation for parsing. Make it easier and quick.
        """

        ## create primary data file
        primary = "%s-primary-sent.log" % uuid.uuid4().__str__()
        primary = os.path.join(self.data_directory, primary)
        os.system('cat %s | grep %s > %s' % (
            self.filepath, self.primary_tag, primary
        ))
        self.primary_data_file = primary

        ## create recruiter data file
        recruiter = "%s-primary-recruiter.log" % uuid.uuid4().__str__()
        recruiter = os.path.join(self.data_directory, recruiter)
        os.system('cat %s | grep %s > %s' % (
            self.filepath, self.recruiter_tag, recruiter
        ))
        self.recruiter_data_file = recruiter

        ## create confirmation data file
        confirm = "%s-primary-confirm.log" % uuid.uuid4().__str__()
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

	    #self.ccount += 1
	    #print "%d/%d" % (self.ccount, self.ctotal)
        except Exception as err:
            ## Log the error with data
            print line, str(err)
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
	    #self.pcount += 1
	    #print "%d/%d" % (self.pcount, self.ptotal)
	    if data["campaign"] == "sendJob":
		self.mailer_tag_log.writelines(['%s\n' % message_id])
        except Exception as err:
            ## Log the error with data
            print line, str(err)
	    #self.mailer_tag_log.writelines(['%s %s\n' % (line, str(err))])

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
		if xuid[0].startswith("sendJob"):
    		    self.recruiter_log.writelines(['%s\n' % message_id])
	except Exception as err:
            print line, str(err)
	    #self.recruiter_log.writelines(['%s %s\n' % (line, str(err))])


    def parse_lines(self):
        """
        Parses a single line of log provided.
        """

	#print "Parsing primary data\n"
        #with open(self.primary_data_file, 'r') as pd_file:
        #    lines = pd_file.readlines()
	#    self.ptotal = len(lines)
	#    self.pcount = 0
        #    for line in lines:
        #        self._parse_message_info(line)

	#print "Parsing recruiter data\n"
        #with open(self.recruiter_data_file, 'r') as rec_file:
        #    lines = rec_file.readlines()
	#    self.rtotal = len(lines)
	#    self.rcount = 0
	#    for line in lines:
	#	self._get_recruiter_info(line)

	#print "Processing ... \n"
        #with open(self.sent_data_file, 'r') as co_file:
        #    lines = co_file.readlines()
	#    self.ctotal = len(lines)
	#    self.ccount = 0
        #    for line in lines:
        #        self._confirm_send(line)
	print "Parsing Data ..."
	lines = self.log_file.readlines()
    	for line in lines:
	    if self.primary_tag in line:
	    	self._parse_message_info(line)
	    elif self.recruiter_tag in line:
	    	self._get_recruiter_info(line)
 	    elif self.confirm_tag in line:
	    	self._confirm_send(line)

    def parse(self):
        if self.log_file:
            #self._prepare()
            self.parse_lines()
	    self._insert()
            self._cleanup()
	return None

    def _insert(self):
        print "Inserting message objects"
        for date, date_obj in self.mongo_data.iteritems():
            for camp, camp_obj in date_obj.iteritems():
                for rec, rec_obj in camp_obj.iteritems():
                    for cid, cid_obj in rec_obj.iteritems():
                        obj = RecruiterMessages(recruiter=rec,
                                date=self.get_date_object(date),
                                campaign=camp,
                                campaign_id=cid,
                                sent=cid_obj.get('sent', 0)
                                )
                        self.final_data.append(obj)

	self.mongo_data.clear()
        RecruiterMessages.objects.insert(self.final_data)
	del self.final_data[:]

    def push_to_mongo(self, mid):

        data = self.data.get(mid)
        date = data.get('sent_at')
        campaign = data.get('campaign', 'nocampaign')
        campaign_id = data.get('campaign_id', 'nocampaignid')
        recruiter_id = data.get('recruiter_id', 'norecruiterid')

        date_data = self.mongo_data.get(date, {})
        camp_data = date_data.get(campaign, {})
        reid_data = camp_data.get(recruiter_id, {})
        caid_data = reid_data.get(campaign_id, {})
        caid_data['sent'] = caid_data.get('sent', 0) + 1
        reid_data[campaign_id] = caid_data
        camp_data[recruiter_id] = reid_data
        date_data[campaign] = camp_data
        self.mongo_data[date] = date_data

	if campaign == "sendJob":
	    self.confirm_log.writelines(['%s\n' % mid])
	    

        del self.data[mid]


class OpenLogParser(BaseLogFileParser):

    def __init__(self, filepath, data_directory="/tmp", date_format="%d/%b/%Y",
            workers=4, *args, **kwargs):

        self.filepath = filepath
        self.data = {}
        self.date_format = date_format

        #Regular expressions
        self.date_regex = r'[\d]+\/[\w]+\/[\d]+'
        self.qs_regex = r'/media/images/dot.gif\?([\w\d=&.@\/\_\-\+\|\%\:]+)'
	self.uemail_regex = r'user_email=([\w\d\+\_\/\=\\\-]+)'

        self.log_file = open(self.filepath, 'r')
	todays_date = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%d_%b_%Y')
	self.open_data_file = open('/tmp/%s_open_data.log' % todays_date, 'w')
        self.workers = workers

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

    def get_normalized_email(email):
        if '@' in email:
            return email
        return self.decrypt(email.replace(" ", "+"))

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
                #print qs_string
                #print qs, tid
                campaign_id = tid[1]
                recruiter_id = tid[-1]

            date_data = self.data.get(cdate, {})
            camp_data = date_data.get(campaign, {})
            recr_data = camp_data.get(recruiter_id, {})
            caid_data = recr_data.get(campaign_id, {})

            caid_data['opened'] = caid_data.get('opened', 0) + 1
            recr_data[campaign_id] = caid_data
            camp_data[recruiter_id] = recr_data
            date_data[campaign] = camp_data

            self.data[cdate] = date_data
	    self.open_data_file.writelines(['%s %s %s %s %s\n' % (cdate, campaign,
		    self.decrypt_aes(user_email), campaign_id, recruiter_id)])
            self.prog += 1
            print "%s/%s" % (self.prog, self.total)
        except Exception as err:
            ## Log the error with data
            print line, str(err)
            #raise

    def update_open_status(self):
        print "Updating opened status\n"
        for date, obj in self.data.iteritems():
            for camp, camp_obj in obj.iteritems():
                for rec, rec_obj in camp_obj.iteritems():
                    for cid, cid_obj in rec_obj.iteritems():
                        message = RecruiterMessages.objects.filter(
                                date=self.get_date_object(date),
                                campaign=camp,
                                recruiter=rec,
                                campaign_id=cid
                                ).first()
                        if message:
			    if message.opened:
                            	message.opened = message.opened + cid_obj.get('opened')
			    else:
                            	message.opened = cid_obj.get('opened')
                            message.save()
	self.data.clear()


class ClickLogParser(BaseLogFileParser):

    def __init__(self, filepath, data_directory="/tmp", date_format="%d/%b/%Y",
            primary_tag="etm_content",
            workers=4, *args, **kwargs):

        self.filepath = filepath
        self.data = {}
        self.date_format = date_format
        self.primary_data_file = None
        self.primary_tag = primary_tag
        self.data_directory = data_directory

        #Regular expressions
        self.date_regex = r'\w{3}\s+\d{1,2}'
        self.qs_regex = r'[\?]([\w\d\=\&\/\-\_\.\%\:\+\?\|\@]+)'

	todays_date = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%d_%b_%Y')
	self.click_data_file = open('/tmp/%s_click_data.log' % todays_date, 'w')

        self.log_file = open(self.filepath, 'r')
        self.workers = workers

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
            qs_string = re.findall(self.qs_regex, line)[-1]
            qs = urlparse.parse_qs(urllib.unquote(qs_string))
            campaign = self.get_normalized_campaign(qs.get('utm_campaign')[0])
            cdate = self.get_normalized_cdate(qs.get('etm_content')[0])
	    user_email = self.get_normalized_email(qs.get('etm_content')[0])
            campaign_id = 'nocampaignid'
            recruiter_id = 'norecruiterid'

            if 'tid' in qs:
                tid = urllib.unquote(qs.get('tid')[0]).split('|')
                campaign_id = tid[1]
                recruiter_id = tid[-1]


            data['campaign_id'] = campaign_id
            data['recruiter_id'] = recruiter_id

            date_data = self.data.get(cdate, {})
            camp_data = date_data.get(campaign, {})
            recr_data = camp_data.get(recruiter_id, {})
            caid_data = recr_data.get(campaign_id, {})

            caid_data['clicked'] = caid_data.get('clicked', 0) + 1
            recr_data[campaign_id] = caid_data
            camp_data[recruiter_id] = recr_data
            date_data[campaign] = camp_data

            self.data[cdate] = date_data
            self.prog += 1

	    self.click_data_file.writelines(['%s %s %s %s %s\n' % (cdate, campaign,
		    user_email, campaign_id, recruiter_id)])

            print "%s/%s" % (self.prog, self.total)
        except Exception as err:
            ## Log the error with data
            print line, str(err)
            self.errors += 1

    def update_click_status(self):
        print "Updating click status\n"
        for date, obj in self.data.iteritems():
            for camp, camp_obj in obj.iteritems():
                for rec, rec_obj in camp_obj.iteritems():
                    for cid, cid_obj in rec_obj.iteritems():
                        message = RecruiterMessages.objects.filter(
                                date=self.get_date_object(date),
                                campaign=camp,
                                recruiter=rec,
                                campaign_id=cid
                                ).first()
                        if message:
			    if message.clicked:
                            	message.clicked = message.clicked + cid_obj.get('clicked')
			    else:
                            	message.clicked = cid_obj.get('clicked')
                            message.save()

	self.data.clear()
