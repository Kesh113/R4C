from django.urls import path

from .views import robots_view


urlpatterns = [
    path('v1/robots/', robots_view, name='robots'),
]
