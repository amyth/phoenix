#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 01-03-2017
# @last_modify: Fri Mar 17 11:28:07 2017
##
########################################

import datetime

from django.conf import settings

import MySQLdb

from .core import BaseBackend


class MySQLBaseBackend(BaseBackend):

    def __init__(self, *args, **kwargs):

        super(MySQLBaseBackend, self).__init__(self, *args, **kwargs)
        self.month_brackets = {
            'jan_mar': range(1, 4),
            'apr_jun': range(4, 7),
            'jul_sep': range(7, 10),
            'oct_dec': range(10, 13)
        }
        self._prepare()

    def _prepare(self):
        self._create_table()

    def _create_table(self):
        yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).date()
        tablename = self._get_tablename(yesterday.month, yesterday.year)
        query = """
            CREATE TABLE IF NOT EXISTS %s (
                sno INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                email CHAR(128) NULL,
                date DATETIME NULL,
                job_ids CHAR(128) NULL,
                job_scores CHAR(128) NULL,
                subject CHAR(255) NULL,
                recruiter_id CHAR(128) NULL,
                campaign_id CHAR(128) NULL) ENGINE=MyISAM DEFAULT CHARACTER SET=utf8;
        """ % (tablename)
        self.cursor.execute(query)

    def _get_month_bracket(self, month):
        for bracket, values in self.month_brackets.iteritems():
            if month in values:
                return bracket
        raise ValueError('Could not get month bracket for month {}'.format(
                month))

    def _get_tablename(self, month, year):
        return "{}_{}_{}".format(self.tablename, self._get_month_bracket(month),
                year)

    def _prepare(self):
        try:
            self.db = MySQLdb.connect(settings.MYSQL_PARSER_SETTINGS.get('host'),
                    settings.MYSQL_PARSER_SETTINGS.get('username'),
                    settings.MYSQL_PARSER_SETTINGS.get('password'),
                    settings.MYSQL_PARSER_SETTINGS.get('database'))
            self.cursor = self.db.cursor()
        except Exception as err:
            print "There was an error connecting to MySQL database: %s" % (
                    str(err))

    def _destroy(self):
        self.db.close()

    def _insert(self):
        self._destroy()


class MySQLInsertSents(MySQLBaseBackend):

    def __init__(self, *args, **kwargs):
        self.tablename = 'mail_sent'
        super(MySQLInsertSents, self).__init__(self, *args, **kwargs)

    def _insert(self, data):
        self._destroy()


class MySQLInsertOpens(MySQLBaseBackend):

    def _insert(self, data):
        self._destroy()


class MySQLInsertClicks(MySQLBaseBackend):

    def _insert(self, data):
        self._destroy()


class MySQLSentParser(object):

    def parse(self):
        pass
