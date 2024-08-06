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