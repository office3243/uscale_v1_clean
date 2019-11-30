from django.shortcuts import render, get_object_or_404, redirect
from .models import Loading, LoadingWeight
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, DetailView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
import datetime
from django.db.models import Q
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required


class LoadingAddView(LoginRequiredMixin, CreateView):

    model = Loading
    template_name = "loadings/add.html"
    fields = ("dealer", "vehicle_details", "extra_info", "created_on")
    success_url = reverse_lazy("loadings:list")

    def form_valid(self, form):
        if Loading.objects.filter(loading_no=form.instance.loading_no).exists():
            messages.warning(self.request, "Loading Number already exists!")
            return super().get(self.request)
        loading = form.save()
        return redirect(loading.get_entries_url)


@login_required
def entries(request, id):
    loading = get_object_or_404(Loading, id=id)
    weight_formset = inlineformset_factory(Loading, LoadingWeight, fields=("material", "weight_count"), extra=1)
    if request.method == "POST":
        formset = weight_formset(request.POST, instance=loading)
        if formset.is_valid():
            formset.save()
            print(request.POST)
            if request.POST.get('entries_done'):
                loading.status = "ED"
                loading.save()
                return redirect("loadings:list")
            return redirect(loading.get_entries_url)
    else:
        formset = weight_formset(instance=loading)
        # print(formset, 555)
        return render(request, "loadings/entries.html", {'formset': formset})


class LoadingListView(LoginRequiredMixin, ListView):

    model = Loading
    template_name = "loadings/list.html"
    context_object_name = "loadings"
    ordering = "-id"

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     return qs.filter(Q(status="PN") | Q(created_on__date__gte=datetime.date.today()+datetime.timedelta(days=-30)))


class LoadingDetailView(LoginRequiredMixin, DetailView):

    model = Loading
    slug_url_kwarg = "id"
    slug_field = "id"
    context_object_name = "loading"
    template_name = "loadings/detail.html"

    def get_object(self, queryset=None):
        loading = super().get_object()
        loading.save()
        return loading
