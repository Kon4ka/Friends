# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
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
        FriendRequest.objects.create(from_user=request.user, to_user=friend)
        return redirect('home')
    else:
        friends = User.objects.all()
        return render(request, 'add_friend.html', {'friends': friends})


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