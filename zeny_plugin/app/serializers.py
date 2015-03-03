from rest_framework import serializers
from .models import User, Storage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('account_id', 'userid',)


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = ('nameid', 'amount', 'refine', 'attribute', 'card0', 'card1', 'card2', 'card3',)
