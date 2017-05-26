#!/usr/bin/python
# -*- coding: <encoding name> -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Tue Nov 15 18:04:43 2016
##
########################################


import datetime
import mongoengine


class RecruiterMessages(mongoengine.Document):

    recruiter = mongoengine.StringField()
    date = mongoengine.DateTimeField()
    campaign = mongoengine.StringField()
    campaign_id = mongoengine.StringField()
    sent = mongoengine.IntField()
    opened = mongoengine.IntField()
    clicked = mongoengine.IntField()
    primary_clicks = mongoengine.IntField(default=0)
