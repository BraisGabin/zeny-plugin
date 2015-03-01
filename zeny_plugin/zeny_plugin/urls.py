from django.conf.urls import patterns, include, url
from django.contrib import admin
from plugin import views

urlpatterns = patterns('',
    url(r'^user/me/storage/$', views.StorageList.as_view(), name='storage-list'),
    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
)
