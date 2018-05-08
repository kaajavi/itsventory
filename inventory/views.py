# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.db.models import Count, Sum, FloatField
from django.db.models.functions import Cast
from django.conf import settings

import json
from django.utils.timezone import datetime, timedelta, make_aware

from django.db.models import Sum

from .models import *

from django.contrib.auth.decorators import user_passes_test

def check_user(user):
    if not user.id:
        return False
    return True


@user_passes_test(check_user, login_url='/')
def item_informe(request):    
    return render(request, 'item_report.html')
    

@user_passes_test(check_user, login_url='/')
def get_categories(request):
    if request.user.is_anonymous:
        return JsonResponse({"detail": "Authentication credentials were not provided."})
    try:
        inventory_id = request.GET['id_inventory']
        qs_categories = Category.objects.filter(inventory__id = inventory_id)
        serialized_categories = json.dumps(list(qs_categories.values('id', 'title')),
                                                cls=DjangoJSONEncoder)
        return JsonResponse(serialized_categories, safe=False)
    except Exception as e:
        return HttpResponse(e)

@user_passes_test(check_user, login_url='/')
def get_places(request):
    if request.user.is_anonymous:
        return JsonResponse({"detail": "Authentication credentials were not provided."})
    try:
        inventory_id = request.GET['id_inventory']
        qs_places = Place.objects.filter(inventory__id = inventory_id)
        serialized_places = json.dumps(list(qs_places.values('id', 'title')),
                                                cls=DjangoJSONEncoder)
        return JsonResponse(serialized_places, safe=False)
    except Exception as e:
        return HttpResponse(e)
