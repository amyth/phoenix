#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 01-03-2017
# @last_modify: Mon Apr 24 16:28:33 2017
##
########################################

import datetime


class BaseBackend(object):

    def __init__(self, *args, **kwargs):
        self._prepare()

    def _prepare(self):
        pass

    def get_date_object(self, date):
        return datetime.datetime.strptime(date, '%b %d %Y')

    def insert_sents(self):
        raise NotImplementedError('`insert_sents` method for this backend is not defined.')

    def insert_opens(self):
        raise NotImplementedError('`insert_opens` method for this backend is not defined.')

    def insert_clicks(self):
        raise NotImplementedError('`insert_clicks` method for this backend is not defined.')

