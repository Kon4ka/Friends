# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView

# from openapi_django.openapi_utils.decorators import openapi

from .models import FriendRequest, FriendRequest, Friend
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegisterUserForm
from .serializers import FriendRequestSerializer, UserSerializer, UserSerializerPassword


class RegisterUser(generics.CreateAPIView):
    form_class = RegisterUserForm
    template_name = "register.html"
    success_url = reverse_lazy("login")
    serializer_class = UserSerializerPassword

    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            },
        ),
        responses={
            201: openapi.Response('Created', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'username': openapi.Schema(type=openapi.TYPE_STRING),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                },
            )),
            400: 'Bad Request',
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

@api_view(['GET', 'POST'])
@swagger_auto_schema(
    operation_description="Add a friend or accept a friend request",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['friend_id'],
        properties={
            'friend_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="The id of the user to add as a friend"),
        },
    ),
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'msg': openapi.Schema(type=openapi.TYPE_STRING, description="A message indicating the result of the operation"),
            },
        )),
        400: 'Bad Request',
    },
)
def add_friend(request):
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        friend = User.objects.get(id=friend_id)
        # Проверяем, есть ли уже такая запись в базе данных
        friend_request = FriendRequest.objects.filter(from_user=request.user, to_user=friend).first()
        # Если записи нет, то проверяем, есть ли обратная заявка
        if not friend_request:
            # Если есть обратная заявка, то принимаем ее, добавляем в друзья и удаляем из базы данных
            reverse_request = FriendRequest.objects.filter(from_user=friend, to_user=request.user).first()
            if reverse_request:
                reverse_request.accept()
                reverse_request.delete()
                return HttpResponse(data={"msg": "Вы добавили друга"})
            # Иначе ничего не делаем и перенаправляем на профиль
            else:
                FriendRequest.objects.create(from_user=request.user, to_user=friend)
                return HttpResponse(data={"msg": "Вы отправили заявку в друзья"})
        # Иначе показываем сообщение об ошибке
        else:
            return HttpResponse(data={"msg": "Такая заявка уже существует"})
    else:
        friends = User.objects.all()
        return render(request, 'add_friend.html', {'friends': friends})

@swagger_auto_schema(
    method='delete',
    operation_description="Delete a friend",
    manual_parameters=[
        openapi.Parameter(
            name='friend_id',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
            description="The id of the user to delete as a friend",
        ),
    ],
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'msg': openapi.Schema(type=openapi.TYPE_STRING, description="A message indicating the result of the operation"),
            },
        )),
        404: 'Not Found',
    },
)
@api_view(['DELETE'])
def delete_friend(request, friend_id):
    # Получаем объект друга по его id
    friend = get_object_or_404(User, id=friend_id)
    # Удаляем текущего пользователя из друзей друга
    Friend.lose_friend(friend, request.user)
    # Удаляем друга из друзей текущего пользователя
    Friend.lose_friend(request.user, friend)
    return HttpResponse(data={"msg": "Вы удалили друга"})

@swagger_auto_schema(
    method='get',
    operation_description="Get the friend request status for a user",
    manual_parameters=[
        openapi.Parameter(
            name='name',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            description="The username of the user to check the friend request status for",
        ),
    ],
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'current_user': openapi.Schema(type=openapi.TYPE_STRING, description="The username of the current user"),
                'friend_user': openapi.Schema(type=openapi.TYPE_STRING, description="The username of the friend user"),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description="The friend request status"),
            },
        )),
        404: 'Not Found',
    },
)
@api_view(['GET'])
def friend_request_status(request, name):
    # Ищем пользователя по имени
    try:
        user = User.objects.get(username=name)
    except User.DoesNotExist:
        return HttpResponse("Пользователь не найден")
    # Ищем заявку на дружбу от или к этому пользователю
    try:
        friend_request = FriendRequest.objects.filter(from_user=user).first() or FriendRequest.objects.filter(to_user=user).first()
    except FriendRequest.DoesNotExist:
        friend_request = None
    # Определяем статус заявки
    if friend_request is None:
        status = "Не отправлена"
    elif not friend_request.status:
        status = "На рассмотрении"
    else:
        status = "Вы друзья"
    # Отдаем статус в html
    print(request.user,user )
    return render(request, 'friend_request_status.html', {'current_user': request.user, 'friend_user': user, 'status': status})


class AcceptFriendRequestView(LoginRequiredMixin, View):

    @swagger_auto_schema(
        method='get',
        operation_description="Accept a friend request",
        manual_parameters=[
            openapi.Parameter(
                name='q',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="The id of the user who sent the friend request",
            ),
        ],
        responses={
            200: openapi.Response('Success', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'msg': openapi.Schema(type=openapi.TYPE_STRING, description="A message indicating the result of the operation"),
                },
            )),
            404: 'Not Found',
        },
    )
    @api_view(['GET'])
    def get(self, request, q):
        # Получаем параметр q из url
        friend_id = q
        # print(friend_id)
        # # Ищем заявку в друзья в базе данных по id отправителя и получателя
        friend_request = get_object_or_404(FriendRequest, from_user=friend_id, to_user=request.user, status=False)
        # # Принимаем заявку в друзья
        friend_request.accept()
        # # Добавляем запись в таблице Friends
        Friend.make_friend(request.user, friend_request.from_user)
        # Перенаправляем пользователя на страницу с друзьями
        return HttpResponse(data={"msg": "Вы приняли заявку на дружбу"})

class LoginFormView(ObtainAuthToken):
    form_class = AuthenticationForm
    template_name = "login.html"
    success_url = reverse_lazy("home")
    serializer_class = UserSerializerPassword

    @swagger_auto_schema(
        method='post',
        operation_description="Log in a user and return a token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
            },
        ),
        responses={
            200: openapi.Response('Success', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING,
                                            description="The authentication token for the user"),
                },
            )),
            400: 'Bad Request',
        },
    )
    @api_view(['POST'])
    def post(self, request, *args, **kwargs):
        return super(LoginFormView, self).post(request, *args, **kwargs)

class CustomLoginFormView(ObtainAuthToken):
    form_class = AuthenticationForm
    template_name = "login.html"
    success_url = reverse_lazy("home")

    @swagger_auto_schema(
        operation_description="Авторизация пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Имя пользователя"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="Пароль пользователя"),
            },
            required=["username", "password"]
        ),
        responses={
            200: openapi.Response("Вы успешно вошли в систему", openapi.Schema(type=openapi.TYPE_OBJECT)),
            401: openapi.Response("Неверное имя пользователя или пароль", openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return HttpResponse(data={"msg": "Вы успешно вошли в систему"})
        else:
            return HttpResponse(data={"msg": "Неверное имя пользователя или пароль"})

class ProfileView(ListAPIView):
    # Указываем модель, из которой берем данные
    model = User
    # Указываем шаблон, в который передаем данные
    template_name = 'accounts/profile.html'
    # Указываем имя переменной, в которой хранятся данные
    context_object_name = 'friends'
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Добавить друга",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "friend_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Идентификатор друга"),
            },
            required=["friend_id"]
        ),
        responses={
            201: openapi.Response("Вы успешно добавили друга", openapi.Schema(type=openapi.TYPE_OBJECT)),
            400: openapi.Response("Неверный идентификатор друга", openapi.Schema(type=openapi.TYPE_OBJECT)),
            401: openapi.Response("Вы не авторизованы", openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def get_queryset(self):
        # Получаем текущего пользователя
        # print((self.request.user))
        try:
            friend = Friend.objects.get(current_user=self.request.user)
            friends = friend.users.all()
        except Friend.DoesNotExist:
            friends = []

        # Используем метод filter вместо get
        friend = Friend.objects.filter(current_user=self.request.user).first()
        if friend:
            friends = friend.users.all()
        else:
            friends = []
        return friends

class FriendRequestListView(ListAPIView):
  # Этот класс наследует от ListView и отображает список запросов в друзья для текущего пользователя
  model = FriendRequest # Указываем модель, из которой берем данные
  template_name = 'friend_request_list.html' # Указываем шаблон, который используем для отображения
  context_object_name = 'friend_requests' # Указываем имя переменной, которая будет содержать список запросов
  serializer_class = FriendRequestSerializer

  @swagger_auto_schema(
    operation_description="Получить список запросов в друзья для текущего пользователя",
    responses={
      200: openapi.Response("Список запросов", FriendRequestSerializer(many=True)),
      401: openapi.Response("Вы не авторизованы", openapi.Schema(type=openapi.TYPE_OBJECT)),
    }
  )
  def get_queryset(self):
    # Этот метод фильтрует запросы по получателю, который является текущим пользователем
    # и по статусу, который равен True (открыт)
    return FriendRequest.objects.filter(to_user=self.request.user, status=False)


@swagger_auto_schema(
    method='GET',
    operation_description="Отклонить заявку в друзья по ее id",
    manual_parameters=[
        openapi.Parameter('request_id', openapi.IN_PATH, description="Идентификатор заявки", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Response("Вы успешно отклонили заявку", openapi.Schema(type=openapi.TYPE_OBJECT)),
        404: openapi.Response("Заявка с таким идентификатором не найдена", openapi.Schema(type=openapi.TYPE_OBJECT)),
        401: openapi.Response("Вы не авторизованы", openapi.Schema(type=openapi.TYPE_OBJECT)),
        405: openapi.Response("Метод не поддерживается", openapi.Schema(type=openapi.TYPE_OBJECT)),
    }
)
@api_view(['GET', 'POST'])
def decline_request_view(request, request_id):
    # Эта вьюшка отклоняет заявку в друзья по ее id
    if request.method == 'GET':
        print(request_id)
        # Получаем заявку из базы данных или возвращаем 404
        friend_request = get_object_or_404(FriendRequest, from_user=request_id)
        # Проверяем, что получатель заявки является текущим пользователем
        if friend_request.to_user == request.user:
            # Отклоняем заявку
            friend_request.delete()
        # Перенаправляем на страницу входящих заявок
        return redirect('requests')
    else:
        # Если метод не POST, то показываем ошибку 405
        return HttpResponseNotAllowed(['GET'])


class OutRequestsView(ListView):
    # Этот класс наследует от ListView и отображает список исходящих заявок от текущего пользователя
    model = FriendRequest # Указываем модель, из которой берем данные
    template_name = 'out_requests.html' # Указываем шаблон, который используем для отображения
    context_object_name = 'out_requests' # Указываем имя переменной, которая будет содержать список заявок
    # serializer_class = FriendRequestSerializer

    @swagger_auto_schema(
        operation_description="Получить список исходящих заявок от текущего пользователя",
        responses={
            200: openapi.Response("Список заявок", FriendRequestSerializer(many=True)),
            401: openapi.Response("Вы не авторизованы", openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    def get_queryset(self):
        # Этот метод фильтрует заявки по отправителю, который является текущим пользователем
        return FriendRequest.objects.filter(from_user=self.request.user)

    @swagger_auto_schema(
        method='POST',
        operation_description="Удалить исходящую заявку по ее id",
        manual_parameters=[
            openapi.Parameter('request_id', openapi.IN_FORM, description="Идентификатор заявки",
                              type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: openapi.Response("Вы успешно удалили заявку", openapi.Schema(type=openapi.TYPE_OBJECT)),
            404: openapi.Response("Заявка с таким идентификатором не найдена",
                                  openapi.Schema(type=openapi.TYPE_OBJECT)),
            401: openapi.Response("Вы не авторизованы", openapi.Schema(type=openapi.TYPE_OBJECT)),
            405: openapi.Response("Метод не поддерживается", openapi.Schema(type=openapi.TYPE_OBJECT)),
        }
    )
    @api_view(['POST'])
    def post(self, request, *args, **kwargs):
        # Этот метод обрабатывает POST-запрос на удаление заявки.
        # Получаем id заявки из POST-данных
        request_id = request.POST.get('request_id')
        # Получаем заявку из базы данных
        friend_request = FriendRequest.objects.get(id=request_id)
        # Проверяем, что отправитель заявки является текущим пользователем
        if friend_request.from_user == request.user:
            # Удаляем заявку из базы данных
            friend_request.delete()
        # Перенаправляем на страницу исходящих заявок
        return redirect('out_requests')
