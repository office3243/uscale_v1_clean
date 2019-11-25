from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.urls import reverse_lazy
from .models import RateGroup, GroupMaterialRate
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.models import inlineformset_factory



class RatesView(LoginRequiredMixin, TemplateView):
    template_name = "rates/rates_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['rate_groups'] = RateGroup.objects.filter(is_active=True)
        return context


class RateGroupListView(LoginRequiredMixin, ListView):
    model = RateGroup
    context_object_name = "rate_groups"
    template_name = "rates/rate_groups/list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True)


class RateGroupDetailView(LoginRequiredMixin, DetailView):
    model = RateGroup
    template_name = "rates/rate_groups/detail.html"
    slug_field = "id"
    slug_url_kwarg = "id"
    context_object_name = "rate_group"
    # def get_object(self, queryset=None):
    #     party = super().get_object()
    #     if party.is_active:
    #         return party
    #     return Http404("Rate Group Is Not Active")


class RateGroupAddView(LoginRequiredMixin, CreateView):
    model = RateGroup
    template_name = "rates/rate_groups/add.html"
    fields = ("name", "extra_info")
    success_url = reverse_lazy('rates:rate_group_list')

    def form_valid(self, form):
        messages.success(self.request, "Rate Group Created Successfully")
        return super().form_valid(form)


class RateGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = RateGroup
    template_name = "rates/rate_groups/update.html"
    slug_field = "id"
    slug_url_kwarg = "id"
    context_object_name = "rate_group"
    fields = ("name", "extra_info")
    success_url = reverse_lazy('rates:rate_group_list')


# @login_required
# def material_rates(request, rate_group_id):
#
#     rate_group = get_object_or_404(RateGroup, id=id, is_active=True)
#     MaterialRateFormSet = inlineformset_factory(RateGroup, GroupMaterialRate, form=WeightForm, extra=0, can_delete=False)
#     if request.method == "POST":
#         formset = MaterialRateFormSet(request.POST, instance=rate_group)
#         if formset.is_valid():
#             formset.save()
#             return redirect(rate_group.get_absolute_url)
#     formset = MaterialRateFormSet(instance=rate_group)
#     context = {"rate_group": rate_group, "formset": formset}
#     return render(request, "rates/rate_groups/material_rate_update.html", context)

class MaterialRateUpdateView(LoginRequiredMixin, UpdateView):

    model = GroupMaterialRate
    template_name = "rates/material_rates/update.html"
    fields = ("material", "amount")
    success_url = reverse_lazy("rates:rate_group_list")
    slug_url_kwarg = "id"
    slug_field = "id"

    def form_valid(self, form):
        self.success_url = form.instance.rate_group.get_absolute_url
        messages.success(self.request, "Rate Update Successfully")
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        print(555)
        return redirect(self.object.rate_group.get_absolute_url)
