from django.urls import path
from .views import *

urlpatterns = [
    path('person/details/', PersonalDetailsView.as_view()),
    path('person/details/<int:pk>/', PersonalDetailsView.as_view()),
    path('person/filtered/', FilteredPersonDetailsView.as_view()),
    path('cities/', CityListView.as_view(), name='city-list'),
    path('states/', StateListView.as_view(), name='state-list'),
    path('PoliceStationCount', PoliceStationCount.as_view()),
    path('PersonCount', PersonCount.as_view()),
    path('multiple-photos/', MultiplePhotosView.as_view(), name='multiple-photos'),
    path('multiple-photos/<int:pk>/', MultiplePhotosView.as_view(), name='person-photos'),
    path('search', search_person, name='search_person'),
    path('police-stations/', PoliceStation_details.as_view(), name='police-station-list'),
    path('police-stations/<int:pk>/', PoliceStation_details.as_view(), name='police-station-detail'),
    path('allpersons/', PersonalDetailsListAPIView.as_view(), name='person_list_api'),
    path('allstations/', PoliceStationLocationListAPIView.as_view(), name='station_list_api'),
    path('complaints/', PoliceComplaintListAPIView.as_view(), name='complaint_list_api'),
    path('complaints/<int:pk>/', PoliceComplaintDetailAPIView.as_view(), name='complaint_detail_api'),
    path('complaintCount/' , complaintsCount.as_view(), name='complaint_count'),
    path('MissingEventDetail/',MissingEventDetailAPIView.as_view(), name='missing_event'),
    path('MissingEventDetail/<int:pk>/', MissingEventDetailAPIView.as_view(), name='complaint_detail_api'),
    
]

