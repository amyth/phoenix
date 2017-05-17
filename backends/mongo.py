#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 01-03-2017
# @last_modify: Wed Apr 26 14:38:16 2017
##
########################################


from .core import BaseBackend
from apps.messages.documents import RecruiterMessages



class MongoBackend(BaseBackend):

    def insert_sents(self, data):
	print "Inserting to Mongo. Please wait .."
	mongo_data = []
        for date, date_obj in data.iteritems():
            for camp, camp_obj in date_obj.iteritems():
                for rec, rec_obj in camp_obj.iteritems():
                    for cid, cid_obj in rec_obj.iteritems():
                        obj = RecruiterMessages(recruiter=rec,
                                date=self.get_date_object(date),
                                campaign=camp,
                                campaign_id=cid,
                                sent=cid_obj.get('sent', 0)
                                )
                        mongo_data.append(obj)

	## Performs bulk insert to mongo. The return statement will free up
	## memory being taken by `mongo_data` object as it is a local variable.
	RecruiterMessages.objects.insert(mongo_data)
	print "Mongo insertion successfully completed.\n"
        return None

    def insert_opens(self, data):
	print "Updating opens in mongoDB"
        for date, obj in data.iteritems():
            for camp, camp_obj in obj.iteritems():
                for rec, rec_obj in camp_obj.iteritems():
                    for cid, cid_obj in rec_obj.iteritems():
                        message = RecruiterMessages.objects.filter(
                                date=self.get_date_object(date),
                                campaign=camp,
                                recruiter=rec,
                                campaign_id=cid
                                ).first()
                        if message:
			    if message.opened:
                            	message.opened = message.opened + cid_obj.get(
                                        'opened')
			    else:
                            	message.opened = cid_obj.get('opened')
                            message.save()

	print "Opens successfully updated in mongoDB\n"
	return None

    def insert_clicks(self, data):
	print "Updating clicks in mongoDB"
	for date, obj in data.iteritems():
            for camp, camp_obj in obj.iteritems():
                for rec, rec_obj in camp_obj.iteritems():
                    for cid, cid_obj in rec_obj.iteritems():
                        message = RecruiterMessages.objects.filter(
                                date=self.get_date_object(date),
                                campaign=camp,
                                recruiter=rec,
                                campaign_id=cid
                                ).first()
                        if message:
			    if message.clicked:
                            	message.clicked = message.clicked + cid_obj.get('clicked')
			    else:
                            	message.clicked = cid_obj.get('clicked')
                                message.primary_clicks = cid_obj.get('primary_action', 0)
                            message.save()

	print "Clicks successfully updated in mongoDB\n"
        return None
