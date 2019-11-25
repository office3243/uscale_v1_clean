from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse_lazy
from .models import Party, Wallet, WalletAdvance
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class PartyListView(LoginRequiredMixin, ListView):
    model = Party
    context_object_name = "parties"
    template_name = "parties/list.html"
    ordering = "-id"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True)


class PartyAddView(LoginRequiredMixin, CreateView):

    model = Party
    fields = ("name", "rate_type", "rate_group", "address", "phone", "whatsapp", "email", "is_wallet_party", "extra_info")
    template_name = "parties/add.html"
    success_url = reverse_lazy('parties:list')

    def form_valid(self, form):
        party = form.save()
        messages.success(self.request, "Party Created Successfully {}".format(party.party_code))
        return super().form_valid(form)


class PartyDetailView(LoginRequiredMixin, DetailView):
    model = Party
    template_name = "parties/detail.html"
    slug_field = "party_code"
    slug_url_kwarg = "party_code"

    def get_object(self, queryset=None):
        party = super().get_object()
        if party.is_active:
            return party
        return Http404("Party Is Not Active")


class PartyUpdateView(LoginRequiredMixin, UpdateView):
    model = Party
    template_name = "parties/update.html"
    fields = ("rate_group", "rate_type", "is_wallet_party")
    slug_field = "party_code"
    slug_url_kwarg = "party_code"
    success_url = reverse_lazy('parties:list')

    def get_object(self, queryset=None):
        party = super().get_object()
        if party.is_active:
            return party
        return Http404("Party Is Not Active")


class WalletListView(LoginRequiredMixin, ListView):

    model = Wallet
    template_name = "parties/wallet_list.html"
    context_object_name = "wallets"
    ordering = "-id"


class WalletDetailView(LoginRequiredMixin, DetailView):
    model = Wallet
    template_name = "parties/wallet_detail.html"
    context_object_name = "wallet"
    slug_field = "id"
    slug_url_kwarg = "id"
