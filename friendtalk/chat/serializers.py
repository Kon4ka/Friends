from django.contrib.auth.models import User
from rest_framework import serializers


from .models import FriendRequest

class FriendRequestSerializer(serializers.ModelSerializer):
    # Этот класс наследует от ModelSerializer и автоматически генерирует поля по модели
    class Meta:
        model = FriendRequest # Указываем модель, для которой создаем сериализатор
        fields = ['id', 'from_user', 'to_user', 'timestamp', 'status'] # Указываем, какие поля модели хотим сериализовать

class UserSerializer(serializers.ModelSerializer):
    # Этот класс наследует от ModelSerializer и автоматически генерирует поля по модели
    class Meta:
        model = User # Указываем модель, для которой создаем сериализатор
        fields = ['id', 'username', 'email', 'first_name', 'last_name'] # Указываем, какие поля модели хотим сериализовать