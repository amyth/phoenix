#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 25-10-2016
# @last_modify: Wed Nov 16 13:51:59 2016
##
########################################

import json

from django.http import HttpResponse

from apps.messages.documents import RecruiterMessages


def campaigns(request):
    results = []
    query = request.GET.get('query', '')
    if query:
        messages = RecruiterMessages.objects.filter(campaign__istartswith=query)
        results = [{'name': x.campaign} for x in messages]

    return HttpResponse(json.dumps(results), content_type='application/json')

