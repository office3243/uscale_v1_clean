from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import BankAccount
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy


class BankAccListView(ListView, LoginRequiredMixin):

    template_name = "bank_accounts/list.html"
    model = BankAccount
    context_object_name = "bank_accounts"
    ordering = "-id"


class BankAccAddView(CreateView, LoginRequiredMixin):

    template_name = "bank_accounts/add.html"
    model = BankAccount
    fields = ("party", "acc_no", "bank_name", "ifsc_code", "branch_name", "account_holder")
    success_url = reverse_lazy("bank_accounts:list")
