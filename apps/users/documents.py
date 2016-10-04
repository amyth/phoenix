#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Tue Oct  4 14:21:10 2016
##
########################################


import mongoengine


UTYPES = (
    (1, 'Recipient'),
    (2, 'Sender')
)


class User(mongoengine.Document):
    """
    Represents a user object document.
    """

    email = mongoengine.StringField()
    uid = mongoengine.StringField()
    utype = mongoengine.IntField(required=True, default=1,
            unique_with=['email', 'uid'], choices=UTYPES)
