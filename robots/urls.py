from django.urls import path

from .views import robot


urlpatterns = [
    path('v1/robots/', robot, name='robot'),
]
