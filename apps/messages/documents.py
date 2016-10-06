#!/usr/bin/python
# -*- coding: <encoding name> -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Thu Oct  6 09:48:54 2016
##
########################################


import datetime
import mongoengine

from apps.campaigns.documents import Campaign
from apps.users.documents import User, Recruiter


class Message(mongoengine.Document):

    sender = mongoengine.ReferenceField(Recruiter, dbref=True)
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
        data["sender"] = {"uid": self.sender.uid}
        data["recipient"] = {
                "email": self.recipient.email,
                "uid": self.recipient.uid
        }
        data["campaign"] = {"name": self.campaign.name}
