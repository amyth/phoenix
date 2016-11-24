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

import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from scripts.parser.mail import MailLogParser


class Command(BaseCommand):

    help = "Downloads and parses the sent mail logs"

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            action='store',
            dest='date',
            default='',
            help='SMTP log file date'
        )
        parser.add_argument(
            '--amz_date',
            action='store',
            dest='amz_date',
            default='',
            help='Amazon log file date'
        )

    def handle(self, *args, **kwargs):

        self.import_files(**kwargs)
        files = self.get_log_files()
        for f in files:
	    if f.endswith('.gz'):
		script = os.path.join(settings.BASE_DIR, "scripts/bash/unzip_files.sh")
		subprocess.call([script, f])
		f = f[:-3]
            parser = MailLogParser(filepath=f)
            parser.parse()
	    os.remove(f)

        print "All done"

    def import_files(self, **kwargs):
	_date = kwargs.get('date')
	_amz = kwargs.get('amz_date')

	script_comm = "scripts/bash/import_mail.sh"
        script = os.path.join(settings.BASE_DIR, script_comm)
	if (_date and _amz):
	    script_list = [script, _date, _amz]
	else:
	    script_list = [script]
        subprocess.call(script_list)

    def get_log_files(self):
        """
        Returns the filepaths to be processed.
        """
        files = []
        file_list = os.listdir(settings.LOG_DATA_DIR)
        for x in file_list:
            if x.startswith('mail'):
                name = os.path.abspath(os.path.join(settings.LOG_DATA_DIR, x))
                files.append(name)
        return files

