from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'planetCode', 'tags', 'profile', 
                 'gender', 'phone', 'email', 'userStatus', 'createTime']
        read_only_fields = ['createTime']