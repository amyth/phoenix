#!/usr/bin/python
# -*- coding: <encoding name> -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Mon Oct  3 15:39:00 2016
##
########################################


import datetime
import mongoengine


class Message(mongoengine.Document):

    sender = mongoengine.ReferenceField(User, required=True, dbref=True)
    recipient = mongoengine.ReferenceField(User, required=True, dbref=True)
    campaign = mongoengine.ReferenceField(Campaign, required=True, dbref=True)

    ## Analytical attributes
    opened = mongoengine.BooleanField(default=False)
    clicked = mongoengine.BooleanField(default=False)
    bounced = mongoengine.BooleanField(default=False)
    sent_at = mongoengine.DateTimeField()
    opened_at = mongoengine.DateTimeField()
    clicked_at = mongoengine.DateTimeField()

    ## Backend fields
    created_at = mongoengine.DateTimeField(default=datetime.datetime.now())


    def to_json(self):
        data = self.to_mongo()
        data["sender"] = {"email": self.sender.email, "uid": self.sender.uid}
        data["recipient"] = {
                "email": self.recipient.email,
                "uid": self.recipient.uid
        }
        data["campaign"] = {"name": self.campaign.name}
