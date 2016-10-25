#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 25-10-2016
# @last_modify: Tue Oct 25 15:31:11 2016
##
########################################

from django.conf.urls import url

from .views import campaign_list_view

urlpatterns = [
    url(r'^j/campaigns/$', campaign_list_view, name="j_campaigns")
]
