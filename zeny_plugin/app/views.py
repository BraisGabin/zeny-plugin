from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .models import User, Storage
from .serializers import UserSerializer, StorageSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        if pk == 'me':
            self.kwargs['pk'] = self.request.user.pk
        elif self.request.user.pk != int(pk):
            raise PermissionDenied()
        return super(UserDetail, self).get(request, *args, **kwargs)


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
