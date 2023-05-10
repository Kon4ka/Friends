# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import FriendRequest, Friend

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}} # скрываем пароль от чтения

    def create(self, validated_data):
        # переопределяем метод create, чтобы хешировать пароль при создании пользователя
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        # проверяем, что имя пользователя и пароль совпадают с данными в базе данных
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            # если пользователь существует и активен, то создаем или получаем токен для него
            token, created = Token.objects.get_or_create(user=user)
            # добавляем токен в возвращаемые данные
            data['token'] = token.key
            return data
        else:
            # если пользователь не существует или не активен, то выбрасываем исключение
            raise serializers.ValidationError("Неверное имя пользователя или пароль")

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user', 'timestamp', 'status')

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ('id', 'users', 'current_user')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')