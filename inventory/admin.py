# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import *
from inv_admin.item_admin import *

admin.site.register(Inventory)
admin.site.register(Place)
admin.site.register(Category)
admin.site.register(Item, ItemAdmin)
