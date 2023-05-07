from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from .forms import RegisterUserForm

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = "register.html"
    success_url = reverse_lazy("login")