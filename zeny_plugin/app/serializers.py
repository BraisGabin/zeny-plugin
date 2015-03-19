from django.conf import settings
from rest_framework import serializers

from .models import User, Char, Storage, Vending


def not_zero(value):
    if value == 0:
        raise serializers.ValidationError('Can\'t be 0.')


class CharSerializer(serializers.ModelSerializer):
    class Meta:
        model = Char
        fields = ('id', 'name',)


class CharFameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Char
        fields = ('id', 'name', 'fame')


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
    zeny = serializers.IntegerField(
        min_value=-settings.MAX_ZENY,
        max_value=settings.MAX_ZENY,
        validators=[
            not_zero,
        ])


class BuySerializer(serializers.Serializer):
    nameid = serializers.IntegerField(min_value=0)
    refine = serializers.IntegerField(min_value=0)
    card0 = serializers.IntegerField(min_value=0)
    card1 = serializers.IntegerField(min_value=0)
    card2 = serializers.IntegerField(min_value=0)
    card3 = serializers.IntegerField(min_value=0)
    amount = serializers.IntegerField(
        min_value=1,
        max_value=settings.MAX_AMOUNT
    )
    zeny = serializers.IntegerField(
        min_value=1,
        max_value=settings.MAX_ZENY,
    )

    def validate(self, data):
        if data['amount'] * data['zeny'] > settings.MAX_ZENY:
            raise serializers.ValidationError("amount x zeny > %d" % settings.MAX_ZENY)
        return data
