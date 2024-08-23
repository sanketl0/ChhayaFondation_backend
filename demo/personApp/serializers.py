from .models import *
from rest_framework import serializers

class multiplePhotosSerializers(serializers.ModelSerializer):
    class Meta:
        model = Multiple_Photos
        fields = '__all__'

class personDetailsSerializers(serializers.ModelSerializer):

    class Meta:
        model = Personal_Details
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Personal_Details
        fields = ['city']

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personal_Details
        fields = ['state']

class police_stationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Police_Station_Location
        fields = '__all__'

class PoliceComplaintSerializer(serializers.ModelSerializer):
    person_name_id = serializers.PrimaryKeyRelatedField(queryset=Personal_Details.objects.all(), source='person_name')
    police_station_name_id = serializers.PrimaryKeyRelatedField(queryset=Police_Station_Location.objects.all(), source='police_station_name')

    person_name = serializers.CharField(source='person_name.person_name', read_only=True)
    police_station_name = serializers.CharField(source='police_station_name.police_station_name', read_only=True)
    class Meta:
        model = Police_Complaint_Details
        fields = [
            'id', 'person_name_id', 'person_name', 'fir_number',
            'police_station_name_id', 'police_station_name',
            'associate_police_officer_name', 'designation', 'fir_upload'
        ]

    def validate_person_name_id(self, value):
        if Police_Complaint_Details.objects.filter(person_name_id=value.id, is_deleted=False).exists():
            raise serializers.ValidationError("This person already has an active complaint registered.")
        return value

    def create(self, validated_data):
        return Police_Complaint_Details.objects.create(**validated_data)

class MissingEventDetailsSerializer(serializers.ModelSerializer):
    person_name_id = serializers.PrimaryKeyRelatedField(queryset=Personal_Details.objects.all(), source='person_name')
    person_name = serializers.CharField(source='person_name.person_name', read_only=True)
    missing_time_formatted = serializers.SerializerMethodField()
    class Meta:
        model = Missing_Event_Details
        fields = '__all__'

    def get_missing_time_formatted(self, obj):
        if obj.missing_time:
            return obj.missing_time.strftime('%I:%M %p')
        return None
