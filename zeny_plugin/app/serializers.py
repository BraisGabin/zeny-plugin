from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from .models import User, Char, Storage, Vending


def not_zero(value):
    if value == 0:
        raise serializers.ValidationError('Can\'t be 0.')


class CharSerializer(serializers.ModelSerializer):
    class Meta:
        model = Char
        fields = ('id', 'name',)


class MyCharSerializer(serializers.ModelSerializer):
    class Meta:
        model = Char
        fields = ('id', 'name', 'zeny',)


class UserSerializer(serializers.ModelSerializer):
    chars = MyCharSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'zeny', 'chars',)


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = ('nameid', 'amount', 'refine', 'card0', 'card1', 'card2', 'card3',)


class VendingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vending
        fields = ('nameid', 'amount', 'refine', 'card0', 'card1', 'card2', 'card3', 'zeny')


class VendingSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Vending
        fields = ('nameid', 'refine', 'card0', 'card1', 'card2', 'card3', 'zeny')


class ZenySerializer(serializers.Serializer):
    zeny = serializers.IntegerField(validators=[
        MaxValueValidator(settings.MAX_ZENY),
        MinValueValidator(-settings.MAX_ZENY),
        not_zero,
    ])
