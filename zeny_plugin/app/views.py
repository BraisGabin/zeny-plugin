from rest_framework import generics, serializers, views
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User, Storage, Vending
from .serializers import UserSerializer, StorageSerializer, VendingSerializer


class UserMe(views.APIView):
    def initial(self, request, *args, **kwargs):
        super(UserMe, self).initial(request, *args, **kwargs)

        pk = self.kwargs['pk']
        if pk == 'me':
            self.kwargs['pk'] = self.request.user.pk
        elif self.request.user.pk != int(pk):
            raise PermissionDenied()


class UserDetail(UserMe, generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return super(UserDetail, self).get(request, *args, **kwargs)


class StorageList(UserMe, generics.ListAPIView):
    serializer_class = StorageSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        self.queryset = Storage.objects.filter(account_id=pk)
        return super(StorageList, self).get(request, *args, **kwargs)


class VendingList(UserMe, generics.ListCreateAPIView):
    serializer_class = VendingSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        self.queryset = Vending.objects.filter(account_id=pk)
        return super(VendingList, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        items = serializer.data
        if len(items) == 0:
            raise serializers.ValidationError('No items.')
        check_no_repeated_items(items)
        Storage.objects.check_items(self.request.user, items)
        Storage.objects.move_items(self.request.user, items)
        return Response(None, status=204)


def check_no_repeated_items(items):
    keys = ['nameid', 'refine', 'card0', 'card1', 'card2', 'card3']
    for i in range(0, len(items)):
        for j in range(i + 1, len(items)):
            a = items[i]
            b = items[j]
            duplicated = True
            for key in keys:
                if a[key] != b[key]:
                    duplicated = False
                    break
            if duplicated:
                raise serializers.ValidationError('Repeated item.')
