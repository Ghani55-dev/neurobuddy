from rest_framework import viewsets
from .models import EntertainmentVideo
from .serializers import VideoSerializer

class VideoViewSet(viewsets.ModelViewSet):
    queryset = EntertainmentVideo.objects.all()
    serializer_class = VideoSerializer