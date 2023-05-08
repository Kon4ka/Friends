# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import FriendRequest, FriendRequest, Friend
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegisterUserForm


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = "register.html"
    success_url = reverse_lazy("login")

def add_friend(request):
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        friend = User.objects.get(id=friend_id)
        # Проверяем, есть ли уже такая запись в базе данных
        friend_request = FriendRequest.objects.filter(from_user=request.user, to_user=friend).first()
        print(0)
        # Если записи нет, то проверяем, есть ли обратная заявка
        if not friend_request:
            print(15)
            # Если есть обратная заявка, то принимаем ее, добавляем в друзья и удаляем из базы данных
            reverse_request = FriendRequest.objects.filter(from_user=friend, to_user=request.user).first()
            if reverse_request:
                reverse_request.accept()
                reverse_request.delete()
                return redirect('profile')
                print(1)
            # Иначе ничего не делаем и перенаправляем на профиль
            else:
                FriendRequest.objects.create(from_user=request.user, to_user=friend)
                return redirect('profile')
        # Иначе показываем сообщение об ошибке
        else:
            return HttpResponse('Такая заявка уже существует')
    else:
        friends = User.objects.all()
        print(6)
        return render(request, 'add_friend.html', {'friends': friends})

def delete_friend(request, friend_id):
    # Получаем объект друга по его id
    friend = get_object_or_404(User, id=friend_id)
    # Удаляем текущего пользователя из друзей друга
    Friend.lose_friend(friend, request.user)
    # Удаляем друга из друзей текущего пользователя
    Friend.lose_friend(request.user, friend)
    return redirect('profile')

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
        return redirect('profile')

class LoginFormView(LoginView):
    form_class = AuthenticationForm
    template_name = "login.html"
    success_url = reverse_lazy("home")

class CustomLoginFormView(FormView):
    form_class = AuthenticationForm
    template_name = "login.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class ProfileView(ListView):
    # Указываем модель, из которой берем данные
    model = User
    # Указываем шаблон, в который передаем данные
    template_name = 'accounts/profile.html'
    # Указываем имя переменной, в которой хранятся данные
    context_object_name = 'friends'

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

class FriendRequestListView(ListView):
  # Этот класс наследует от ListView и отображает список запросов в друзья для текущего пользователя
  model = FriendRequest # Указываем модель, из которой берем данные
  template_name = 'friend_request_list.html' # Указываем шаблон, который используем для отображения
  context_object_name = 'friend_requests' # Указываем имя переменной, которая будет содержать список запросов

  def get_queryset(self):
    # Этот метод фильтрует запросы по получателю, который является текущим пользователем
    # и по статусу, который равен True (открыт)
    return FriendRequest.objects.filter(to_user=self.request.user, status=False)

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

    def get_queryset(self):
        # Этот метод фильтрует заявки по отправителю, который является текущим пользователем
        return FriendRequest.objects.filter(from_user=self.request.user)

    def post(self, request, *args, **kwargs):
        # Этот метод обрабатывает POST-запрос на удаление заявки
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
