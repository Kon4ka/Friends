from django.contrib.auth.models import User
from rest_framework import serializers


from .models import FriendRequest, Friend

class FriendRequestSerializer(serializers.ModelSerializer):
    # Этот класс наследует от ModelSerializer и автоматически генерирует поля по модели
    class Meta:
        model = FriendRequest # Указываем модель, для которой создаем сериализатор
        fields = ['id', 'from_user', 'to_user', 'timestamp', 'status'] # Указываем, какие поля модели хотим сериализовать

class UserSerializer(serializers.ModelSerializer):
    # Этот класс наследует от ModelSerializer и автоматически генерирует поля по модели
    class Meta:
        model = User # Указываем модель, для которой создаем сериализатор
        fields = ['id', 'username', 'email', 'first_name'] # Указываем, какие поля модели хотим сериализовать

class UserSerializerPassword(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class FriendSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    current_user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Friend
        fields = ["id", "users", "current_user"]

    def create(self, validated_data):
        friend = Friend.objects.create(current_user=validated_data["current_user"])
        return friend

    def update(self, instance, validated_data):
        instance.users.set(validated_data.get("users", instance.users))
        instance.save()
        return instance