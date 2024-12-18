from django.contrib import admin
from django.urls import path

from orders.views import order_process
from robots.views import robots_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/robots/', robots_view, name='robots'),
    path('api/v1/to-book-robot/', order_process, name='to-book-robot')
]
