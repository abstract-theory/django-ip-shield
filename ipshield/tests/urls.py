import django
if django.VERSION[0] >= 2:
    from django.urls import re_path as version_url_path
else:
    from django.conf.urls import url as version_url_path

from ..views import LimitIps_as_view

eventName = "test-hello-template"
blockTime = 5
findTime = 5
maxAllowed = 10


urlpatterns = [
    version_url_path(r'^test-hello-template/$', LimitIps_as_view(eventName, blockTime, findTime, maxAllowed, template_name='hello-template.html')),
]
