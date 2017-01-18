#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 06-10-2016
# @last_modify: Wed Nov 16 13:59:07 2016
##
########################################

import datetime
import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from scripts.parser.mail import (
        OpenLogParser,
        ClickLogParser
)


class Command(BaseCommand):

    help = "Tracks the mail opens through the log files."

    def add_arguments(self, parser):
        parser.add_argument(
            '--start_date',
            action='store',
            dest='start_date',
            default='',
            help='Log file start date'
        )
        parser.add_argument(
            '--end_date',
            action='store',
            dest='end_date',
            default='',
            help='Log file end date'
        )

    def handle(self, *args, **kwargs):
        self.import_files(**kwargs)
        self.track_opens()
        self.track_clicks()

        print "All done"

    def import_files(self, **kwargs):
	start_date = kwargs.get('start_date')
	end_date = kwargs.get('end_date')
	script_comm = "scripts/bash/import_openclick.sh"
        script = os.path.join(settings.BASE_DIR, script_comm)

        if (start_date and end_date):
            try:
                start_date_real = datetime.datetime.strptime(start_date, '%Y%m%d')
                end_date_real = datetime.datetime.strptime(end_date, '%Y%m%d')
            except Exception as err:
                raise CommandError('Wrong date format provided for start/end date. Please use \'YYYYMMDD\' format.')

            if start_date_real > end_date_real:
                raise CommandError('Start date cannot be greater than end date.')

            all_dates = [ start_date_real + datetime.timedelta(n) for n in range(int ((end_date_real - start_date_real).days))]

            for day in all_dates:
                date_string = day.strftime('%Y%m%d')
                script_list = [script, date_string]
                subprocess.call(script_list)
	else:
	    script_list = [script]
            subprocess.call(script_list)

    def track_opens(self):
        files = self.get_open_log_files()
        for f in files:
	    if f.endswith('.gz'):
                script = os.path.join(settings.BASE_DIR, "scripts/bash/unzip_files.sh")
                subprocess.call([script, f])
                f = f[:-3]
            parser = OpenLogParser(filepath=f)
            parser.parse()

    def track_clicks(self):
        files = self.get_click_log_files()
        for f in files:
	    if f.endswith('.gz'):
                script = os.path.join(settings.BASE_DIR, "scripts/bash/unzip_files.sh")
                subprocess.call([script, f])
                f = f[:-3]
            parser = ClickLogParser(filepath=f)
            parser.parse()

    def get_open_log_files(self):
        """
        Returns the filepaths to be processed.
        """
        files = []
        file_list = os.listdir(settings.LOG_DATA_DIR)
        for x in file_list:
            if x.startswith('track'):
                name = os.path.abspath(os.path.join(settings.LOG_DATA_DIR, x))
                files.append(name)
        return files

    def get_click_log_files(self):
        """
        Returns the filepaths to be processed.
        """
        files = []
        file_list = os.listdir(settings.LOG_DATA_DIR)
        for x in file_list:
            if x.startswith('httpd'):
                name = os.path.abspath(os.path.join(settings.LOG_DATA_DIR, x))
                files.append(name)
        return files
