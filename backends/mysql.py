#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 01-03-2017
# @last_modify: Wed May  3 16:27:43 2017
##
########################################

import datetime

from django.conf import settings

import MySQLdb

from .core import BaseBackend


class MySQLMergeBackend(BaseBackend):

    def __init__(self, *args, **kwargs):

        self.month_brackets = {
            'jan_mar': range(1, 4),
            'apr_jun': range(4, 7),
            'jul_sep': range(7, 10),
            'oct_dec': range(10, 13)
        }

        ## Define required tablename prefixes
        self.sents_table_prefix = 'mail_sent'
        self.opens_table_prefix = 'mail_opened'
        self.clicks_table_prefix = 'mail_clicked'
        super(MySQLMergeBackend, self).__init__(self, *args, **kwargs)

    def _create_table(self, tablename):
        query = """
            CREATE TABLE IF NOT EXISTS %s (
                sno INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                email CHAR(128) NULL,
                action_date DATETIME NULL,
                job_ids CHAR(128) NULL,
                job_scores CHAR(128) NULL,
                subject CHAR(255) NULL,
                device CHAR(255) NULL,
                recruiter_id CHAR(128) NULL,
                primary_action BOOLEAN NOT NULL DEFAULT 0,
                endpoint CHAR(255) NULL,
                campaign CHAR(255) NULL,
                campaign_date DATETIME NULL,
                campaign_id CHAR(128) NULL) ENGINE=MyISAM DEFAULT CHARACTER SET=utf8;
        """ % (tablename)
        self.cursor.execute(query)
        pass

    def _get_month_bracket(self, month):
        for bracket, values in self.month_brackets.iteritems():
            if month in values:
                return bracket
        raise ValueError('Could not get month bracket for month {}'.format(
                month))

    def _get_tablename(self, prefix):
        yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).date()
        return "{}_{}_{}".format(prefix, self._get_month_bracket(
                yesterday.month), yesterday.year)

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

        ## Create required tables if they dont exist
        self.create_sents_table()
        self.create_opens_table()
        self.create_clicks_table()


    def _destroy(self):
        self.db.close()

    def _insert(self):
        self._destroy()

    def create_sents_table(self):
        tablename = self._get_tablename(self.sents_table_prefix)
        self._create_table(tablename)

    def create_opens_table(self):
        tablename = self._get_tablename(self.opens_table_prefix)
        self._create_table(tablename)

    def create_clicks_table(self):
        tablename = self._get_tablename(self.clicks_table_prefix)
        self._create_table(tablename)

    def insert_sents(self, data):
        tablename = self._get_tablename(self.sents_table_prefix)
        self._insert(tablename, data)
        self._destroy()

    def insert_opens(self, data):
        tablename = self._get_tablename(self.opens_table_prefix)
        self._insert(tablename, data)
        self._destroy()

    def insert_clicks(self, data):
        tablename = self._get_tablename(self.clicks_table_prefix)
        self._insert(tablename, data)
        self._destroy()

    def _process_data(self, data):
        mysql_data = []
        for date, date_obj in data.iteritems():
            for camp, camp_obj in date_obj.iteritems():
                for rec, rec_obj in camp_obj.iteritems():
                    for cid, cid_obj in rec_obj.iteritems():
			obj = [cid_obj.get('email', ''),
				self.get_date_object(date),
                                cid_obj.get('job_ids', ''),
                                cid_obj.get('job_scores',''),
                                cid_obj.get('subject', ''),
                                cid_obj.get('device', ''),
                                rec,
                                cid_obj.get('primary_action', 0),
                                cid_obj.get('endpoint', ''),
                                camp,
                                self.get_date_object(cid_obj.get('campaign_date')),
                                cid
				]
                        mysql_data.append(obj)
        return mysql_data

    def _insert(self, tablename, data):
        data = self._process_data(data)
        print "Insert data to MySql (%s)" % tablename
        insert_statement = "INSERT INTO %s " % tablename
        query = insert_statement + """ (email, action_date, job_ids, job_scores, subject, device, recruiter_id, primary_action, endpoint, campaign, campaign_date, campaign_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        self.cursor.executemany(query, data)
        print "Data successfully entered to MySql (%s)" % tablename
