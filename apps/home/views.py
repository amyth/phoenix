#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 17-10-2016
# @last_modify: Wed Nov 16 13:42:05 2016
##
########################################

from collections import OrderedDict
import datetime

from django.conf import settings
from django.contrib import messages as django_messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView
from django.utils import timezone

from apps.messages.documents import RecruiterMessages
from .predicates import is_allowed_campaign

import rules


class IndexView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        if self.request.method == 'POST':
            request = self.request
            sdate = request.POST.get('start_date')
            edate = request.POST.get('end_date')
            cams = request.POST.get('selected')
            camp_id = request.POST.get('camp_id')
            uid = request.POST.get('sent_by')
	    main_data, messages = self.get_numbers(sdate=sdate, edate=edate,
                    cams=cams, camp_id=camp_id, uid=uid)
            context['main_data'] = main_data
        else:
	    selected_data = {}
	    main_data, messages = self.get_numbers()
            context["main_data"] = main_data
       	    selected_data['start_date'] = (timezone.now() + timezone.timedelta(days=-1)).strftime('%a %b %d %Y')
	    context['selected_data'] = selected_data

	#campaigns = list(set([m.campaign for m in messages if not m.campaign.startswith('RevivalEmails_')]))
	campaigns = list(set([m.campaign for m in messages]))
	context['campaigns'] = [{'name':c} for c in campaigns]

        return context

    def get_numbers(self, sdate=None, edate=None, cams=None, camp_id=None, uid=None):
	restricted_campaigns = []
        results = []
        query_filter = {}

        sdate = self.format_date(sdate) if sdate else datetime.datetime.now() + datetime.timedelta(days=-1)
        edate = self.format_date(edate) if edate else None

        if cams:
	    #if cams == "RevivalEmails":
	    #    query_filter['campaign__istartswith'] = "RevivalEmails"
	    #else:
            	cams = cams.split(',')
		allowed_cams = []
		for cam in cams:
		    if rules.test_rule('is_allowed_campaign', self.request.user, cam):
			allowed_cams.append(cam)
		    else:
			restricted_campaigns.append(cam)

		
		if restricted_campaigns:
		    django_messages.error(self.request,
			    'You do not have permission to access the mentioned campaign(s): %s' % ', '.join(restricted_campaigns)) 
            	query_filter['campaign__in'] = allowed_cams
	else:
		admins = Group.objects.get(name='administrators')
		if admins not in self.request.user.groups.all():
		    user_group = self.request.user.groups.first()
		    allowed_cams = settings.CAMPAIGN_PERMISSIONS.get(user_group.name, [])
		    query_filter['campaign__in'] = allowed_cams
	
        if sdate:
            if not edate:
		sdate = timezone.datetime.strptime(sdate.strftime('%D'), '%m/%d/%y')
		start_time = sdate.replace(hour=0, minute=0, second=0)
		end_time = sdate.replace(hour=23, minute=59, second=59)
                query_filter['date__gte'] = start_time
                query_filter['date__lte'] = end_time
            else:
                query_filter['date__gte'] = sdate
                query_filter['date__lte'] = edate

        if camp_id:
            query_filter['campaign_id'] = camp_id

        if uid:
            query_filter['recruiter'] = uid

	message_qs = RecruiterMessages.objects.filter(**query_filter)
        messages = list(message_qs)
        sent = sum([x.sent for x in messages if x.sent])
        opened = sum([x.opened for x in messages if x.opened])
        clicked = sum([x.clicked for x in messages if x.clicked])
        results.append({'sent': sent})
        results.append({'opened': opened})
        results.append({'clicked': clicked})

	## datewise data
	if (sdate and edate):
	    dw_results = OrderedDict()
	    dates = [sdate + datetime.timedelta(n) for n in range(int((edate - sdate).days)+1)]
	    for d in dates:
		start_time = d.replace(hour=0, minute=0, second=0)
		end_time = d.replace(hour=23, minute=59, second=59)
		filtered = list(message_qs.filter(date__gte=start_time, date__lte=end_time))
		dw_results[d.strftime('%B %d %Y')] = {
		    'sent': sum([x.sent for x in filtered if x.sent]),
		    'opened': sum([x.opened for x in filtered if x.opened]),
		    'clicked': sum([x.clicked for x in filtered if x.clicked]),
		}
	    results.append({'datewise': dw_results})


        return results, messages

    def format_date(self, d):
        return timezone.datetime.strptime(d, '%a %b %d %Y')


    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['selected_data'] = self.get_selected_data(request.POST)
        return super(TemplateView, self).render_to_response(context)

    def get_selected_data(self, post):
        selected_data = {}
        selected = post.get('selected','')
        selected = selected.split(',') if selected else []
        selected_data['selected'] = selected
        selected_data['start_date'] = post.get('start_date')
        selected_data['end_date'] = post.get('end_date')
        selected_data['sent_by'] = post.get('sent_by')

        return selected_data


def logout_view(request):
    logout(request)
    return redirect('/login/')

## View variables
index = login_required(IndexView.as_view())
