from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy


class RegisterView(CreateView):

    form_class = UserCreationForm
    model = User
    template_name = "accounts/register.html"
    success_url = reverse_lazy("portal:home")
