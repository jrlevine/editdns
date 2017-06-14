"""editdns URL Configuration

"""
from django.conf.urls import url, include
from django.contrib import admin
from editapp.views import indexview

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')), # various login and logout URLs
    url(r'^edit/', include('editapp.urls'), name='edit'), # actual stuff in rpc app
    url(r'^edit$', indexview),          # default to index page
    url(r'^$', indexview)               # start in DNS app
]
