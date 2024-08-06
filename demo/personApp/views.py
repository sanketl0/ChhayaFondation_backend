from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Personal_Details, Multiple_Photos
from .serializers import *
from rest_framework.authentication import TokenAuthentication  # this is for authentication for class based views
from rest_framework.permissions import IsAuthenticated 
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.views.decorators.http import require_GET

class PersonalDetailsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Allow any user to access the GET request
        return super().get_permissions()  # Apply default permissions for other methods

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
                    person = Personal_Details.objects.get(pk=pk)
                    serializer = personDetailsSerializers(person)
                    return Response({'data': serializer.data})
                except Personal_Details.DoesNotExist:
                    return Response({'message': 'Person not found'})
            else:
                search_query = request.GET.get('search', '')
                if search_query:
                    details = Personal_Details.objects.filter(
                        Q(person_name__icontains=search_query)
                    ).order_by('-id')
                else:
                    details = Personal_Details.objects.all().order_by('-id')

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
            return Response({'message': f'Something went wrong: {str(e)}'})

    def delete(self, request, pk=None):
        try:
            if pk is not None:
                try:
                    person = Personal_Details.objects.get(pk=pk)
                    person.delete()
                    return Response({'message': 'Person deleted successfully'})
                except Personal_Details.DoesNotExist:
                    return Response({'message': 'Person not found'})
            else:
                return Response({'message': 'Person ID is required for deletion'})
        except Exception as e:
            return Response({'message': f'Something went wrong: {str(e)}'})

    def put(self, request, pk):
        try:
            if pk is not None:
                try:
                    person = Personal_Details.objects.get(pk=pk)
                    # Initialize the serializer with partial=False for a complete update
                    serializer = personDetailsSerializers(person, data=request.data, partial=True)

                    if serializer.is_valid():
                        serializer.save()

                        # Handle main photo separately if provided
                        main_photo = request.FILES.get('main_photo')
                        if main_photo:
                            person.main_photo = main_photo

                        person.save()

                        # Save multiple photos if provided
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


# class FilteredPersonDetailsView(APIView):
#     def get(self, request):
#         try:
#             filters = {
#                 'level': request.GET.get('level', ''),
#                 'blood_group': request.GET.get('blood_group', ''),
#                 'gender': request.GET.get('gender', ''),
#                 'state': request.GET.get('state', ''),
#                 'city': request.GET.get('city', '')
#             }
#
#             filter_query = Q()
#             for key, value in filters.items():
#                 if value:
#                     filter_query &= Q(**{key: value})
#
#             search_query = request.GET.get('search', '')
#             if search_query:
#                 filter_query &= Q(person_name__icontains=search_query)
#
#             details = Personal_Details.objects.filter(filter_query).order_by('-id')
#
#             page_size = int(request.GET.get('page_size', 8))
#             paginator = Paginator(details, page_size)
#             page_number = int(request.GET.get('page', 1))
#             page_obj = paginator.get_page(page_number)
#             serializer = personDetailsSerializers(page_obj, many=True)
#
#             return Response({
#                 'data': serializer.data,
#                 'pagination': {
#                     'total_pages': paginator.num_pages,
#                     'current_page': page_obj.number,
#                     'has_next': page_obj.has_next(),
#                     'has_previous': page_obj.has_previous()
#                 }
#             })
#         except Exception as e:
#             return Response({'message': f'Something went wrong: {str(e)}'})


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


@require_GET
def search_person(request):
    name = request.GET.get('name', '').strip()
    if name:
        persons = Personal_Details.objects.filter(person_name__icontains=name)
        results = [{'id': person.id, 'name': person.person_name, 'photo': person.main_photo.url} for person in persons]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})