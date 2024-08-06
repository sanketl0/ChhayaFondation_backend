from django.urls import path
from .views import *

urlpatterns = [
    # class based urls
    path('auth/', AuthViews.as_view())
]
