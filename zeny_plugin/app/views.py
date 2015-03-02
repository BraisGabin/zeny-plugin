from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .models import Storage
from .serializers import StorageSerializer


class StorageList(generics.ListAPIView):
    serializer_class = StorageSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk == 'me':
            pk = self.request.user.pk
        elif self.request.user.pk != int(pk):
            raise PermissionDenied()
        self.queryset = Storage.objects.filter(account_id=pk)
        return super(StorageList, self).get(request, *args, **kwargs)
