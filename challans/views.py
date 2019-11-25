from django.shortcuts import render, get_object_or_404, redirect
from .models import Challan, Weight, WeightEntry, ReportWeight
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, DetailView, ListView
from django.urls import reverse_lazy
from materials.models import Material
from parties.models import Party
from django.http import JsonResponse, Http404
from .forms import ChallanRawCreateForm, WeightForm, ReportWeightForm
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib import messages
from django.utils import timezone
import datetime
from django.db.models import Q
import decimal


class ChallanAddView(LoginRequiredMixin, CreateView):

    model = Challan
    template_name = "challans/add.html"
    fields = ("party", "vehicle_details", "extra_info", "challan_no")
    success_url = reverse_lazy("challans:list")

    def form_valid(self, form):
        if Challan.objects.filter(challan_no=form.instance.challan_no).exists():
            messages.warning(self.request, "Challan Number already exists!")
            return super().get(self.request)
        form.instance.created_by = self.request.user
        challan = form.save()
        return redirect(challan.get_entries_url)


class ChallanListView(LoginRequiredMixin, ListView):

    model = Challan
    template_name = "challans/list.html"
    context_object_name = "challans"
    ordering = "-id"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(Q(status="PN") | Q(created_on__date__gte=datetime.date.today()+datetime.timedelta(days=-30)))


class ChallanEntriesView(LoginRequiredMixin, DetailView):
    template_name = "challans/entries.html"
    model = Challan
    slug_url_kwarg = "challan_no"
    slug_field = "challan_no"

    def get_object(self, queryset=None):
        challan = super().get_object()
        if not challan.is_entries_done:
            return challan
        raise Http404("Challan Entries are Done. Cant be updated now!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["materials"] = Material.objects.filter(is_active=True)
        return context  


@login_required
def entries_submit(request, challan_no):
    challan = get_object_or_404(Challan, challan_no=challan_no)
    if request.method == "POST":
        has_reports = (request.POST['has_reports'] == "Y")
        if not has_reports:
            challan.is_reports_done = True
            challan.is_entries_done = True
            challan.save()
            return redirect(challan.get_assign_rates_url)
        else:
            challan.is_entries_done = True
            challan.save()
            return redirect(challan.get_assign_reports_url)
    else:
        return redirect(challan.get_entries_url)


@login_required
def entries_done(request, challan_no):
    challan = get_object_or_404(Challan, challan_no=challan_no)
    challan.is_entries_done = True
    challan.save()
    return redirect(challan.get_assign_reports_url)


@login_required
def assign_reports(request, challan_no):
    challan = get_object_or_404(Challan, challan_no=challan_no, is_entries_done=True)
    if request.method == "POST":
        report_inputs = [report_input for report_input in request.POST if "report_input" in report_input]
        for report_input in report_inputs:
            try:
                weight_id = report_input.split("__")[-1]
                report_type = request.POST["report_type__" + weight_id]
                weight = get_object_or_404(Weight, challan=challan, id=weight_id)
                weight_count = float(request.POST['report_input__' + weight_id])
                report_weight = ReportWeight.objects.get_or_create(weight=weight)[0]
                report_weight.weight_count = weight_count
                report_weight.report_type = report_type
                report_weight.reported_on = timezone.now()
                report_weight.save()
            except Exception as e:
                print(e)
                pass
        return redirect(challan.get_assign_rates_url)
    else:
        context = {"challan": challan}
        return render(request, "challans/assign_reports.html", context)


@login_required
def assign_rates(request, challan_no):
    challan = get_object_or_404(Challan, challan_no=challan_no, is_entries_done=True)
    if challan.is_rates_assigned:
        return redirect(challan.get_payment_add_url)
    WeightFormSet = inlineformset_factory(Challan, Weight, form=WeightForm, extra=0, can_delete=False)
    if request.method == "POST":
        formset = WeightFormSet(request.POST, instance=challan)
        if formset.is_valid():
            formset.save()
            challan.refresh_weights()
            challan.is_rates_assigned = True
            challan.save()
            return redirect(challan.get_payment_add_url)
    formset = WeightFormSet(instance=challan)
    context = {"challan": challan, "formset": formset}
    return render(request, "challans/assign_rates.html", context)


def recent_entry_delete(request):
    if request.method == "POST":
        challan = get_object_or_404(Challan, challan_no=request.POST['challan_no'], is_entries_done=False)
        recent_entry = challan.get_recent_weight_entry
        recent_entry.delete()
        messages.success(request, "Last Entry Delete Successfullyx")
        return redirect(str(challan.get_entries_url))
    else:
        return redirect("portal:home")


def weight_entry_create(request):

    """
    Weight instance will be get_or_created by passing material_id and challan_id .
    A new instance of WeightEntry model will be created with relation to above Weight instance.
    And material_id will be passed to request param named 'lmtid'
    """
    if request.method == "POST":
        entry = float(request.POST['entry_weight'])
        challan = get_object_or_404(Challan, challan_no=request.POST['challan_no'])
        material_id = request.POST['material_id']
        """dont allow entry less than 0.1"""
        if entry > 0.1:
            material = get_object_or_404(Material, id=material_id)
            weight = Weight.objects.get_or_create(challan=challan, material=material)[0]
            weight_entry = WeightEntry.objects.create(weight=weight, entry=entry)
            try:
                """for fields validation"""
                weight_entry.full_clean()
            except Exception as e:
                messages.warning(request, e)
                weight_entry.delete()
        else:
            messages.warning(request, "Entry Cannot be less than 0.1")
        return redirect(str(challan.get_entries_url) + "?lmtid={}".format(material_id))
    else:
        return redirect("portal:home")


class ChallanDoneView(LoginRequiredMixin, DetailView):

    model = Challan
    slug_url_kwarg = "challan_no"
    slug_field = "challan_no"
    template_name = "challans/done.html"


class ChallanDetailView(LoginRequiredMixin, DetailView):

    model = Challan
    slug_url_kwarg = "challan_no"
    slug_field = "challan_no"
    context_object_name = "challan"
    template_name = "challans/detail.html"

    def get_object(self, queryset=None):
        challan = super().get_object()
        challan.save()
        return challan
