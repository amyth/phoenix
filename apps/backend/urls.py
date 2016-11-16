#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 25-10-2016
# @last_modify: Wed Nov 16 13:48:00 2016
##
########################################

from django.conf.urls import url

from .views import campaigns


urlpatterns = [
    url(r'^j/campaigns$', campaigns, name='campaigns')
]
