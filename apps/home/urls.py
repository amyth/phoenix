#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 17-10-2016
# @last_modify: Mon Oct 17 12:43:14 2016
##
########################################

from django.conf.urls import url

from .views import (
    index,
    logout_view
)

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^u/logout/$', logout_view, name="logout"),
]
