#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 25-10-2016
# @last_modify: Tue Oct 25 17:34:32 2016
##
########################################
import json

from django.http import HttpResponse
from django.views.generic import View

from apps.campaigns.documents import Campaign


class CampaignList(View):
    def get(self, request, *args, **kwargs):
        results = []
        query = request.GET.get('query')
        if query:
            campaigns = Campaign.objects.filter(name__istartswith=query)
            for campaign in campaigns:
                results.append({'name': campaign.name, 'id': str(campaign.id)})
        return HttpResponse(json.dumps(results))


campaign_list_view = CampaignList.as_view()
