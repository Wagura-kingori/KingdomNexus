from django.urls import path
from .api_views import test_api

urlpatterns = [
    path('test/', test_api),
]
