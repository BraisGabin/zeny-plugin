from django.conf.urls import patterns, include, url
from app import views

urlpatterns = patterns('',
    url(r'^user/me/storage/$', views.StorageList.as_view(), name='storage-list'),
    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
)
