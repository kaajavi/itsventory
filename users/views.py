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
from .models import UserProfile

# Create your views here.
def edit_profile(request):
    if request.user.is_anonymous:
        return JsonResponse({"detail": "Authentication credentials were not provided."})
    up = UserProfile.objects.get_or_create(user = request.user)
    return redirect(reverse('admin:users_userprofile_change', args=[up[0].id]))
