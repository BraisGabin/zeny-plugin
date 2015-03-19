import itertools
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import Http404

from rest_framework import generics, serializers, mixins
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .mixins import UserMe
from .models import User, Char, Storage, Vending
from .serializers import UserSerializer, StorageSerializer, VendingSerializer
from zeny_plugin.app.exceptions import ConflictError
from zeny_plugin.app.models import Item
from zeny_plugin.app.permissions import OnlyOwner, BuyOrOnlyOwner
from zeny_plugin.app.serializers import VendingSerializer2, MyCharSerializer, CharSerializer, ZenySerializer, \
    BuySerializer, CharFameSerializer


class UserDetail(UserMe, mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (BuyOrOnlyOwner,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        seller = self.get_object()
        self.serializer_class = BuySerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        buyer = request.user
        buyer.buy(data, seller)
        return Response(status=204)


class CharDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Char.objects.all()
    serializer_class = CharSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        char = self.get_object()
        if char.account_id == request.user.pk:
            self.serializer_class = MyCharSerializer
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *arg, **args):
        char = self.get_object()
        if char.account_id != self.request.user.pk:
            raise PermissionDenied()
        if char.online:
            raise ConflictError("You're connected to the server with the PJ %s, please disconnect and retry."
                                % char.name)
        self.serializer_class = ZenySerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        zeny = serializer.data['zeny']
        char.move_zeny(zeny)
        return Response(status=204)


class FameList(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = CharFameSerializer

    def get(self, request, *args, **kwargs):
        fame = kwargs['fame']
        if fame == 'blacksmith':
            self.queryset = Char.objects.blacksmith_fame()
        elif fame == 'alchemist':
            self.queryset = Char.objects.alchemist_fame()
        else:
            raise Http404()
        return self.list(self, request, *args, **kwargs)


class StorageList(UserMe, mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = StorageSerializer
    permission_classes = (OnlyOwner,)

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
    permission_classes = (OnlyOwner,)

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
