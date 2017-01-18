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

	print 'Calling parse_sent\n'
	call_command('parse_sent', start_date=start_date, end_date=end_date)

	print 'Calling track_activity\n'
	call_command('track_activity', start_date=start_date, end_date=end_date)
