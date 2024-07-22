from django.urls import re_path
from myapp import consumers

websocket_urlpatterns = [
    re_path(r'ws/progress/(?P<ppt_id>[^/]+)/$', consumers.ProgressConsumer.as_asgi()),
]