from rest_framework import serializers
from .models import EntertainmentVideo

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntertainmentVideo
        fields = '__all__'