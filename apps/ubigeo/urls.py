from django.contrib import admin
from django.conf.urls import url
from . import views

app_name="ubigeo"

urlpatterns = [
    url(r'^departamentos/(?P<id>[-\w]+)/$', views.department, name='department'),
    url(r'^provincias/(?P<id>[-\w]+)/$', views.province, name='province'),
    url(r'^distritos/(?P<id>[-\w]+)/$', views.district, name='district'),
]


