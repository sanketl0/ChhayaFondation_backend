from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count
from .serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated 
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from django.views.decorators.http import require_GET

class PersonalDetailsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def post(self, request):
        try:
            data = request.data.copy()
            photos = request.FILES.getlist('photos')
            main_photo = request.FILES.get('main_photo')

            if not data.get('person_name'):
                return Response({'message': 'person name is required'})

            if not main_photo:
                return Response({'message': 'main photo is required'})

            serializer = personDetailsSerializers(data=data)
            if serializer.is_valid():
                person = serializer.save()

                person.main_photo = main_photo
                person.save()

                for photo in photos:
                    Multiple_Photos.objects.create(person_name=person, photos=photo)

                return Response({'message': 'Personal details uploaded successfully'})
            else:
                return Response({'message': serializer.errors})

        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'})

    def get(self, request, pk=None):
        try:
            if pk is not None:
                try:
                    person = Personal_Details.objects.get(pk=pk, is_deleted=False)
                    serializer = personDetailsSerializers(person)
                    return Response({'data': serializer.data})
                except Personal_Details.DoesNotExist:
                    return Response({'message': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                search_query = request.GET.get('search', '')
                if search_query:
                    persons = Personal_Details.objects.filter(
                        Q(name__icontains=search_query) |
                        Q(address__icontains=search_query) |
                        Q(city__icontains=search_query) |
                        Q(state__icontains=search_query) |
                        Q(country__icontains=search_query),
                        is_deleted=False
                    ).order_by('-id')
                else:
                    persons = Personal_Details.objects.filter(is_deleted=False).order_by('-id')

                page_size = int(request.GET.get('page_size', 8))
                paginator = Paginator(persons, page_size)
                page_number = int(request.GET.get('page', 1))
                page_obj = paginator.get_page(page_number)
                serializer = personDetailsSerializers(page_obj, many=True)

                return Response({
                    'data': serializer.data,
                    'pagination': {
                        'total_pages': paginator.num_pages,
                        'current_page': page_obj.number,
                        'has_next': page_obj.has_next(),
                        'has_previous': page_obj.has_previous()
                    }
                })
        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk=None):
        try:
            if pk is not None:
                try:
                    person = Personal_Details.objects.get(pk=pk)
                    person.is_deleted = True
                    person.save()
                    return Response({'message': 'Person marked as deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except Personal_Details.DoesNotExist:
                    return Response({'message': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message': 'Person ID is required for deletion'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            if pk is not None:
                try:
                    person = Personal_Details.objects.get(pk=pk,is_deleted=False)
                    # Initialize the serializer with partial=False for a complete update
                    serializer = personDetailsSerializers(person, data=request.data, partial=True)

                    if serializer.is_valid():
                        serializer.save()

                        # Handle main photo separately if provided
                        main_photo = request.FILES.get('main_photo')
                        if main_photo:
                            person.main_photo = main_photo

                        person.save()
                        photos = request.FILES.getlist('photos')
                        if photos:
                            for photo in photos:
                                Multiple_Photos.objects.create(person_name=person, photos=photo)
                        return Response({'message': 'Personal details updated successfully'})
                    else:
                        return Response({'message': serializer.errors})
                except Personal_Details.DoesNotExist:
                    return Response({'message': 'Person not found'})
            else:
                return Response({'message': 'Person ID is required for update'})
        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'})

class MultiplePhotosView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()
    def get(self, request, pk=None):
        try:
            if pk is not None:
                person_photos = Multiple_Photos.objects.filter(person_name_id=pk)
                if not person_photos.exists():
                    return Response({'message': 'Person not found'}, status=404)
                serializer = multiplePhotosSerializers(person_photos, many=True)
            else:
                photos = Multiple_Photos.objects.all()
                serializer = multiplePhotosSerializers(photos, many=True)
            return Response({'data': serializer.data}, status=200)
        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'}, status=500)

    def post(self, request):
        try:
            files = request.FILES.getlist('photos')
            person_id = request.data.get('person_name_id')
            if not person_id:
                return Response({'message': 'Person ID is required'}, status=400)
            photo_instances = [Multiple_Photos(photos=file, person_name_id=person_id) for file in files]
            Multiple_Photos.objects.bulk_create(photo_instances)
            return Response({'message': 'Photos uploaded successfully'}, status=201)
        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'}, status=500)

class FilteredPersonDetailsView(APIView):
    def get(self, request):
        try:
            search_query = request.GET.get('search', '')
            filters = {
                'level': request.GET.get('level', ''),
                'blood_group': request.GET.get('blood_group', ''),
                'gender': request.GET.get('gender', ''),
                'state': request.GET.get('state', ''),
                'city': request.GET.get('city', '')
            }

            # First filter by person_name if search_query is provided
            if search_query:
                # Filter by person_name
                details = Personal_Details.objects.filter(person_name__icontains=search_query)
            else:
                # If no search_query, start with all objects
                details = Personal_Details.objects.all()

            # Apply additional filters
            for key, value in filters.items():
                if value:
                    details = details.filter(**{key: value})

            # Apply ordering and pagination
            details = details.order_by('-id')
            page_size = int(request.GET.get('page_size', 8))
            paginator = Paginator(details, page_size)
            page_number = int(request.GET.get('page', 1))
            page_obj = paginator.get_page(page_number)
            serializer = personDetailsSerializers(page_obj, many=True)

            return Response({
                'data': serializer.data,
                'pagination': {
                    'total_pages': paginator.num_pages,
                    'current_page': page_obj.number,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            })
        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'}, status=500)

class CityListView(generics.ListAPIView):
    serializer_class = CitySerializer

    def get(self, request, *args, **kwargs):
        cities = Personal_Details.objects.values_list('city', flat=True).distinct()
        return Response(cities)

class StateListView(generics.ListAPIView):
    serializer_class = StateSerializer

    def get(self, request, *args, **kwargs):
        state = Personal_Details.objects.values_list('state', flat=True).distinct()
        return Response(state)

@require_GET
def search_person(request):
    name = request.GET.get('name', '').strip()
    if name:
        persons = Personal_Details.objects.filter(person_name__icontains=name)
        results = [{'id': person.id, 'name': person.person_name, 'photo': person.main_photo.url} for person in persons]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})

class PoliceStation_details(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser,JSONParser]
    def get(self, request, pk=None):
        try:
            if pk is not None:
                try:
                    police_station = Police_Station_Location.objects.get(pk=pk, is_deleted=False)
                    serializer = police_stationSerializer(police_station)
                    return Response({'data': serializer.data})
                except Police_Station_Location.DoesNotExist:
                    return Response({'message': 'Police Station not found'}, status=404)
            else:
                search_query = request.GET.get('search', '')
                if search_query:
                    # Filter police stations based on search query and exclude soft-deleted ones
                    police_stations = Police_Station_Location.objects.filter(
                        (Q(police_station_name__icontains=search_query) |
                         Q(address__icontains=search_query) |
                         Q(city__icontains=search_query) |
                         Q(state__icontains=search_query) |
                         Q(country__icontains=search_query)),
                        is_deleted=False
                    ).order_by('-id')
                else:
                    # Get all police stations excluding soft-deleted ones
                    police_stations = Police_Station_Location.objects.filter(is_deleted=False).order_by('-id')

                page_size = int(request.GET.get('page_size', 8))
                paginator = Paginator(police_stations, page_size)
                page_number = int(request.GET.get('page', 1))
                page_obj = paginator.get_page(page_number)
                serializer = police_stationSerializer(page_obj, many=True)

                return Response({
                    'data': serializer.data,
                    'pagination': {
                        'total_pages': paginator.num_pages,
                        'current_page': page_obj.number,
                        'has_next': page_obj.has_next(),
                        'has_previous': page_obj.has_previous()
                    }
                })
        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'}, status=500)

    def post(self, request):
        serializer = police_stationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            if pk is not None:
                try:
                    police_station = Police_Station_Location.objects.get(pk=pk, is_deleted=False)
                    police_station.is_deleted = True
                    police_station.save()
                    return Response({'message': 'Police Station marked as deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                except Police_Station_Location.DoesNotExist:
                    return Response({'message': 'Police Station not found'}, status=404)
            else:
                return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'}, status=500)

    def put(self, request, pk=None):
        try:
            if pk is not None:
                try:
                    police_station = Police_Station_Location.objects.get(pk=pk, is_deleted=False)
                    serializer = police_stationSerializer(police_station, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
                    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                except Police_Station_Location.DoesNotExist:
                    return Response({'message': 'Police Station not found'}, status=404)
            else:
                return Response({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'}, status=500)

class PoliceStationCount(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            total_count = Police_Station_Location.objects.filter(is_deleted=False).count()
            return Response({'total_count': total_count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class complaintsCount(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            total_counts =Police_Complaint_Details.objects.filter(is_deleted=False).count()
            return Response({'total_count': total_counts}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Something  went wrong: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERRORTTP_500)

class PersonCount(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            total_count = Personal_Details.objects.filter(is_deleted=False).count()
            case_status_counts = Personal_Details.objects.filter(is_deleted=False).values('case_status').annotate(count=Count('case_status'))
            case_status_data = {
                'Pending': 0,
                'Ongoing': 0,
                'Solved': 0,
                'Closed':0
            }

            for status_count in case_status_counts:
                case_status_data[status_count['case_status']] = status_count['count']

            return Response({
                'total_count': total_count,
                'case_status_counts': case_status_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PersonalDetailsListAPIView(APIView):
    def get(self, request):
        persons = Personal_Details.objects.all()
        serializer = personDetailsSerializers(persons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PoliceStationLocationListAPIView(APIView):
    def get(self, request):
        stations = Police_Station_Location.objects.all()
        serializer = police_stationSerializer(stations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PoliceComplaintListAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request):
        complaints = Police_Complaint_Details.objects.filter(is_deleted=False)  # Remove .first()
        if complaints.exists():  # Check if there are complaints
            serializer = PoliceComplaintSerializer(complaints, many=True)  # Serialize as a list
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'No complaints found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        serializer = PoliceComplaintSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PoliceComplaintDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request, pk):
        complaint = Police_Complaint_Details.objects.filter(pk=pk,is_deleted=False).first()
        if complaint:
            serializer = PoliceComplaintSerializer(complaint)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        complaint = Police_Complaint_Details.objects.filter(pk=pk,is_deleted=False).first()
        if not complaint:
            return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PoliceComplaintSerializer(complaint, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        complaint = Police_Complaint_Details.objects.filter(pk=pk, is_deleted=False).first()
        if not complaint:
            return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)

        complaint.is_deleted = True
        complaint.save()
        return Response(status=status.HTTP_204_NO_CONTENT)



# to apis for Get , Post , Put , Delete to add missing details of particular person
class MissingEventDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # this get permission is to implemented for to access data without authentication
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request, pk=None):
        try:
            if pk:
                missing_event = Missing_Event_Details.objects.filter(pk=pk, is_deleted=False).first()
                if missing_event:
                    serializer = MissingEventDetailsSerializer(missing_event)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({'error': 'Missing event details not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                missing_events = Missing_Event_Details.objects.filter(is_deleted=False).order_by('-id')
                page_size = int(request.GET.get('page_size', 4))
                page_number = int(request.GET.get('page', 1))
                paginator = Paginator(missing_events, page_size)
                page_obj = paginator.get_page(page_number)
                serializer = MissingEventDetailsSerializer(page_obj, many=True)
                response_data = {
                    'data': serializer.data,
                    'pagination': {
                        'total_pages': paginator.num_pages,
                        'current_page': page_obj.number,
                        'has_next': page_obj.has_next(),
                        'has_previous': page_obj.has_previous(),
                        'total_entries': paginator.count
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = MissingEventDetailsSerializer(data=request.data)
        try:
            person_name_id = request.data.get('person_name_id')
            if Missing_Event_Details.objects.filter(person_name_id=person_name_id).exists():
                return Response({'error': 'Missing event for this person already exists'},
                                status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, pk):
        try:
            missing_event = Missing_Event_Details.objects.filter(pk=pk, is_deleted=False).first()
            if not missing_event:
                return Response({'error': 'Missing event details not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = MissingEventDetailsSerializer(missing_event, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            if pk:
                missing_event = Missing_Event_Details.objects.filter(pk=pk, is_deleted=False).first()
                if not missing_event:
                    return Response({'error': 'Missing event details not found'}, status=status.HTTP_404_NOT_FOUND)

                missing_event.is_deleted = True
                missing_event.save()
                return Response({'message': f'Missing event {pk} soft deleted successfully.'},
                                status=status.HTTP_204_NO_CONTENT)
            else:
                missing_events = Missing_Event_Details.objects.filter(is_deleted=False)
                if not missing_events.exists():
                    return Response({'error': 'No missing event details to delete'}, status=status.HTTP_404_NOT_FOUND)

                missing_events.update(is_deleted=True)
                return Response({'message': 'All missing events soft deleted successfully.'},
                                status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
















