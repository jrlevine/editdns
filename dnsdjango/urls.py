"""dnsdjango URL Configuration

"""
from django.conf.urls import url, include
from django.contrib import admin
from dnsedit.views import indexview

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')), # various login and logout URLs
    url(r'^dnsedit/', include('dnsedit.urls'), name='dnsedit'), # actual stuff in rpc app
    url(r'^dnsedit$', indexview),       # default to index page
    url(r'^$', indexview)               # start in DNS app
]
