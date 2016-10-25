#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 06-10-2016
# @last_modify: Mon Oct 10 14:17:18 2016
##
########################################

import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from scripts.parser.mail import MailLogParser


class Command(BaseCommand):

    help = "Downloads and parses the sent mail logs"

    def handle(self, *args, **kwargs):
        #self.import_files()
        files = self.get_log_files()
        for f in files:
            parser = MailLogParser(filepath=f)
            parser.parse()

        print "All done"

    def import_files(self):
        script = os.path.join(settings.BASE_DIR, "scripts/bash/import_mail.sh")
        subprocess.call([script])

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

