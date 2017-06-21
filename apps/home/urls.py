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
from django.views.generic import TemplateView

from .views import (
    index,
    track_ads,
    track_imps,
    logout_view
)

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^adverts/$', track_ads, name="trackads"),
    url(r'^impressions/$', track_imps, name="trackimps"),
    url(r'^u/logout/$', logout_view, name="logout"),
    url(r'^jsatabl/$', TemplateView.as_view(template_name="others/jsatabl.html"), name="jsatabl"),
]
