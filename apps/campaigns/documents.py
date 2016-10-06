#!/usr/bin/python
# -*- coding: <encoding name> -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Wed Oct  5 16:49:56 2016
##
########################################


import mongoengine


class Campaign(mongoengine.Document):

    name = mongoengine.StringField(required=True, unique=True)
    cid = mongoengine.StringField()
