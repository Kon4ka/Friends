from django.contrib.auth.models import User
from rest_framework import serializers


from .models import FriendRequest

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