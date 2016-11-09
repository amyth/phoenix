#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Wed Oct  5 14:47:31 2016
##
########################################


import mongoengine


class User(mongoengine.Document):
    """
    Represents a user object document.
    """

    email = mongoengine.StringField()
    uid = mongoengine.StringField()


class Recruiter(mongoengine.Document):

    uid = mongoengine.StringField()
    email = mongoengine.StringField()
