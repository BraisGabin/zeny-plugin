import itertools

from rest_framework import generics, serializers, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .mixins import UserMe
from .models import User, Storage, Vending
from .serializers import UserSerializer, StorageSerializer, VendingSerializer
from zeny_plugin.app.exceptions import ConflictError
from zeny_plugin.app.serializers import VendingSerializer2


class UserDetail(UserMe, mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class StorageList(UserMe, mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = StorageSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        self.queryset = Storage.objects.filter(account_id=pk)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.serializer_class = StorageSerializer
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        items = serializer.data
        if len(items) == 0:
            raise serializers.ValidationError('No items.')
        check_no_repeated_items(items)
        if self.request.user.online:
            raise ConflictError("You're connected to the server. please disconnect and retry.")
        Vending.objects.check_items(self.request.user, items)
        Vending.objects.move_items(self.request.user, items)
        return Response(status=204)


class VendingList(UserMe, mixins.ListModelMixin, generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        self.serializer_class = VendingSerializer
        pk = self.kwargs.get('pk')
        self.queryset = Vending.objects.filter(account_id=pk)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.serializer_class = StorageSerializer
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        items = serializer.data
        if len(items) == 0:
            raise serializers.ValidationError('No items.')
        check_no_repeated_items(items)
        if self.request.user.online:
            raise ConflictError("You're connected to the server. please disconnect and retry.")
        Storage.objects.check_items(self.request.user, items)
        Storage.objects.move_items(self.request.user, items)
        return Response(status=204)

    def put(self, request, *args, **kwargs):
        self.serializer_class = VendingSerializer2
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        items = serializer.data
        if len(items) == 0:
            raise serializers.ValidationError('No items.')
        check_no_repeated_items(items)
        for item in items:
            zeny = item.pop('zeny')
            Vending.objects.filter(**item).update(zeny=zeny)
        return Response(status=204)


def check_no_repeated_items(items):
    if any(check_same_item(*item) for item in itertools.permutations(items, 2)):
        raise serializers.ValidationError('Repeated item.')


def check_same_item(a, b):
    keys = ['nameid', 'refine', 'card0', 'card1', 'card2', 'card3']
    equals = True
    for key in keys:
        if a[key] != b[key]:
            equals = False
            break
    return equals
