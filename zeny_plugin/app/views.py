from rest_framework import generics
from .models import Storage
from .serializers import StorageSerializer


class StorageList(generics.ListAPIView):
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer
