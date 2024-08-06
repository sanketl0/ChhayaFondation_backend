from django.urls import path
from .views import *

urlpatterns = [
    path('person/details/', PersonalDetailsView.as_view()),
    path('person/details/<int:pk>/', PersonalDetailsView.as_view()),
    path('person/filtered/', FilteredPersonDetailsView.as_view()),
    path('api/cities/', CityListView.as_view(), name='city-list'),
    path('multiple-photos/', MultiplePhotosView.as_view(), name='multiple-photos'),
    path('multiple-photos/<int:pk>/', MultiplePhotosView.as_view(), name='person-photos'),
    path('search', search_person, name='search_person'),
]

