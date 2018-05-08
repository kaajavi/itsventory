from django.conf.urls import include, url
from .views import *

urlpatterns = [
	url(r'^get_categories', get_categories, name='get_categories'),
    url(r'^get_places', get_places, name='get_places'),
]
