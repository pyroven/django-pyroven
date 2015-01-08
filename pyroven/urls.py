from django.conf.urls import patterns, url

from pyroven.views import raven_login, raven_logout, raven_return

urlpatterns = patterns(
    '',
    url(r'^login/$', raven_login, name='raven_login'),
    url(r'^logout/$', raven_logout, name='raven_logout'),
    url(r'^raven_return/$', raven_return, name='raven_return'),
)
