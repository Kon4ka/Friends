from django.contrib.auth.models import User
from rest_framework import serializers


from .models import FriendRequest, Friend

class FriendRequestSerializer(serializers.ModelSerializer):
    # ���� ����� ��������� �� ModelSerializer � ������������� ���������� ���� �� ������
    class Meta:
        model = FriendRequest # ��������� ������, ��� ������� ������� ������������
        fields = ['id', 'from_user', 'to_user', 'timestamp', 'status'] # ���������, ����� ���� ������ ����� �������������

class UserSerializer(serializers.ModelSerializer):
    # ���� ����� ��������� �� ModelSerializer � ������������� ���������� ���� �� ������
    class Meta:
        model = User # ��������� ������, ��� ������� ������� ������������
        fields = ['id', 'username', 'email', 'first_name', 'last_name'] # ���������, ����� ���� ������ ����� �������������

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