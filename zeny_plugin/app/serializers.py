from rest_framework import serializers
from .models import User, Char, Storage, Vending


class CharSerializer(serializers.ModelSerializer):
    class Meta:
        model = Char
        fields = ('id', 'name', 'zeny',)


class UserSerializer(serializers.ModelSerializer):
    chars = CharSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'chars',)


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
