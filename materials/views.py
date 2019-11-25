from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse_lazy
from .models import Material
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class MaterialListView(LoginRequiredMixin, ListView):
    model = Material
    context_object_name = "materials"
    template_name = "materials/list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True)


class MaterialDetailView(LoginRequiredMixin, DetailView):
    model = Material
    template_name = "materials/detail.html"
    slug_field = "material_code"
    slug_url_kwarg = "material_code"

    def get_object(self, queryset=None):
        material = super().get_object()
        if material.is_active:
            return material
        return Http404("Material Is Not Active")
