'''
    #  Model admin <=  https://docs.djangoproject.com/es/1.10/_modules/django/contrib/admin/options/#ModelAdmin
    In the after link, see you all configuration and options about model admin.
    Is very important understand the getters:
    +  e.g.:
        get_form(self, request, obj=None,**kwards):
        -  This function, return the especific object. So, you can define more than one forms in your modelForm (remember, forms are defined in .forms.py), and you can return specific form by user type, if the object is new (obj==None) or already had been created.

'''
from django.core.urlresolvers import reverse
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from users.models import User
from inventory.models import *

from django.utils.html import format_html, format_html_join
from material import (Layout, Fieldset, Row, Column, Span,  Field,  # NOQA
                   Span2, Span3, Span4, Span5, Span6, Span7,
                   Span8, Span9, Span10, Span11, Span12,
                   LayoutMixin)
from django.contrib.staticfiles.templatetags.staticfiles import static

from django.template import loader, Context

from django.contrib.admin import SimpleListFilter




class CategoryAdmin(admin.ModelAdmin):
    pass
