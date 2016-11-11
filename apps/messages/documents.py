#!/usr/bin/python
# -*- coding: <encoding name> -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 03-10-2016
# @last_modify: Tue Oct 25 18:23:50 2016
##
########################################


import datetime
import mongoengine


class Message(mongoengine.Document):

    message_id = mongoengine.StringField(dbref=True)
    sender = mongoengine.StringField(dbref=True)
    sender_uid = mongoengine.StringField(dbref=True)
    recipient = mongoengine.StringField(dbref=True)
    campaign = mongoengine.StringField(dbref=True)
    campaign_uid = mongoengine.StringField(dbref=True)
    reply_to = mongoengine.StringField(dbref=True)

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
                "email": self.recipient,
                "uid": self.recipient_uid
        }
        data["campaign"] = {"name": self.campaign, "uid": self.campaign_uid}
