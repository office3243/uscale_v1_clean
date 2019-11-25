from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, DeleteView, DetailView, TemplateView, CreateView
from payments.models import Payment, AccountTransaction, WalletTransaction, CashTransaction
from django.urls import reverse_lazy
from parties.models import Wallet, WalletAdvance
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class ExecutiveRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


class Executive2RequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return (self.request.user.is_superuser or self.request.user.is_staff) and self.request.user.username == "executive2"


class DashboardView(ExecutiveRequiredMixin, TemplateView):
    template_name = "cms_admin/dashboard.html"


class PaymentListView(ExecutiveRequiredMixin, ListView):

    model = Payment
    template_name = "cms_admin/payments/list.html"
    context_object_name = "payments"
    ordering = "-id"


class PaymentDetailView(ExecutiveRequiredMixin, DetailView):

    template_name = "cms_admin/payments/detail.html"
    model = Payment
    context_object_name = "payment"
    slug_field = "id"
    slug_url_kwarg = "id"


class AccountTransactionListView(ExecutiveRequiredMixin, ListView):

    model = AccountTransaction
    template_name = "cms_admin/payments/account_transactions/list.html"
    context_object_name = "account_transactions"
    ordering = "-id"


class AccountTransactionDetailView(ExecutiveRequiredMixin, DetailView):

    model = AccountTransaction
    context_object_name = "account_transaction"
    template_name = "cms_admin/payments/account_transactions/detail.html"
    slug_field = "id"
    slug_url_kwarg = "id"


class AccountTransactionUpdateView(Executive2RequiredMixin, UpdateView):

    model = AccountTransaction
    context_object_name = "account_transaction"
    template_name = "cms_admin/payments/account_transactions/update.html"
    slug_field = "id"
    slug_url_kwarg = "id"
    success_url = reverse_lazy("cms_admin:account_transactions_list")
    fields = ("payment_party", "payed_on", "serial_no")


class WalletListView(ExecutiveRequiredMixin, ListView):

    model = Wallet
    context_object_name = "wallets"
    template_name = "cms_admin/wallets/list.html"
    ordering = "-id"


class WalletAdvanceListView(ExecutiveRequiredMixin, ListView):
    model = WalletAdvance
    context_object_name = "wallet_advances"
    template_name = "cms_admin/wallets/wallet_advances/list.html"
    ordering = "-id"


class WalletAdvanceCreateView(ExecutiveRequiredMixin, CreateView):
    model = WalletAdvance
    template_name = "cms_admin/wallets/wallet_advances/create.html"
    success_url = reverse_lazy("cms_admin:wallet_advances_list")
    fields = ("wallet", "amount", "gateway")


class WalletUpdateView(ExecutiveRequiredMixin, UpdateView):
    model = Wallet
    template_name = "cms_admin/wallets/update.html"
    success_url = reverse_lazy("cms_admin:wallet_list")
    fields = ("deduct_type", "fixed_amount")
    slug_url_kwarg = "id"
    slug_field = "id"