# dnsedit url switcher

from django.conf.urls import url

from . import views

app_name = 'dnsedit'
urlpatterns = [
    url(r'^$', views.indexview, name='index'),
    url(r'^create$', views.createview, name='create'),
    url(r'^edit/([-a-zA-Z0-9._]+)$', views.editview, name='edit'),
    url(r'^editblock/([-a-zA-Z0-9._]+)$', views.editblockview, name='editblock'),
    url(r'^record/([-a-zA-Z0-9._]+)/(\d+)$', views.recordview, name='record'),
    url(r'^recadd/([-a-zA-Z0-9._]+)$', views.recordaddview, name='recordadd'),
    url(r'^test$', views.testview, name='test'),
]