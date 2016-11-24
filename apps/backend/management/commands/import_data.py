#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 06-10-2016
# @last_modify: Wed Nov 16 13:58:49 2016
##
########################################

import datetime
import gc
import os
import subprocess
import syslog
import time

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from scripts.parser.mail import MailLogParser


class Command(BaseCommand):

    help = "Imports the log data for a date range"

    def add_arguments(self, parser):
	parser.add_argument(
	    '--start',
	    action='store',
	    dest='start',
	    default=None,
	    help='start date for parsing logs'
	)
	parser.add_argument(
	    '--end',
	    action='store',
	    dest='end',
	    default=None,
	    help='end date for parsing logs'
	)

    def handle(self, *args, **kwargs):

	start_date = kwargs.get('start')
	end_date = kwargs.get('end')

	if not (start_date and end_date):
	    raise CommandError('Start and end date is required.')
	try:
	    start_date_real = datetime.datetime.strptime(start_date, '%Y%m%d')
	    end_date_real = datetime.datetime.strptime(end_date, '%Y%m%d')
	except Exception as err:
	    raise CommandError('Wrong date format provided for start/end date. Please use \'YYYYMMDD\' format.')

	if start_date_real > end_date_real:
	    raise CommandError('Start date cannot be greater than end date.')

	all_dates = [ start_date_real + datetime.timedelta(n) for n in range(int ((end_date_real - start_date_real).days))]

	for day in all_dates:
	    try:
		date_string = day.strftime('%Y%m%d')
		amazon_date = day.strftime('%b_%-d')
		print 'Starting import for %s\n' % date_string
		print 'Calling parse_sent\n'
		call_command('parse_sent', date=date_string, amz_date=amazon_date)
		gc.collect()
		time.sleep(45)
		print 'Calling track_activity\n'
		call_command('track_activity', date=date_string)
		gc.collect()
		time.sleep(45)
	    except (OSError, Exception) as err:
		gc.collect()
		time.sleep(45)
		syslog.syslog(syslog.LOG_ERR, "PHOENIX: Error while importing data for date: %s : %s" % (day.strftime('%Y%m%d'), str(err)))
