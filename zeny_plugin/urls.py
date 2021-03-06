from django.conf.urls import patterns, include, url
from app import views
from oauth2_provider import views as oauth_views

urlpatterns = patterns(
    '',
    url(r'^user/(?P<pk>[0-9]+|me)/$', views.UserDetail.as_view(), name='user-detail'),
    url(r'^user/(?P<pk>[0-9]+|me)/storage/$', views.StorageList.as_view(), name='storage-list'),
    url(r'^user/(?P<pk>[0-9]+|me)/vending/$', views.VendingList.as_view(), name='vending-list'),
    url(r'^char/(?P<pk>[0-9]+)/$', views.CharDetail.as_view(), name='char-detail'),
    url(r'^fame/(?P<fame>.+)/$', views.FameList.as_view(), name='fame-detail'),
    url(r'^oauth/authorize/$', oauth_views.AuthorizationView.as_view(template_name='authorize.html'), name="authorize"),
    url(r'^oauth/token/$', oauth_views.TokenView.as_view(), name="token"),
    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
)
