#!/usr/bin/python
# -*- coding: utf-8 -*-
#
########################################
##
# @author:          Amyth
# @email:           mail@amythsingh.com
# @website:         www.techstricks.com
# @created_date: 17-10-2016
# @last_modify: Tue Oct 25 18:50:40 2016
##
########################################

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.utils import timezone

from apps.campaigns.documents import Campaign
from apps.messages.documents import Message


class IndexView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        if self.request.method == 'POST':
            request = self.request
            sdate = request.POST.get('start_date')
            edate = request.POST.get('end_date')
            cams = request.POST.get('selected')
            uid = request.POST.get('sent_by')
            context['main_data'] = self.get_numbers(sdate=sdate, edate=edate,
                    cams=cams, uid=uid)
        else:
            context["main_data"] = self.get_numbers()
        context["campaigns"] = Campaign.objects.all()

        return context

    def get_numbers(self, sdate=None, edate=None, cams=None, uid=None):
        results = []
        messages = base_messages = Message.objects.all()

        sdate = self.format_date(sdate) if sdate else timezone.now() + timezone.timedelta(days=-1)
        edate = self.format_date(edate) if edate else None

        if cams:
            cams = Campaign.objects.filter(name__in=cams.split(','))
            base_messages = base_messages.filter(campaign__in=list(cams))

        if sdate:
            if not edate:
                base_messages = base_messages.filter(sent_at=sdate)
            else:
                base_messages = base_messages.filter(sent_at__gte=sdate,
                        sent_at__lte=edate)

        if uid:
            from apps.users.documents import Recruiter
            sender = list(Recruiter.objects.filter(uid=uid))
            base_messages = base_messages.filter(sender__in=sender)

        results.append({'sent': base_messages.count()})
        results.append({'opened': base_messages.filter(opened=True).count()})
        results.append({'clicked': base_messages.filter(clicked=True).count()})

        return results

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



## View variables
index = login_required(IndexView.as_view())
