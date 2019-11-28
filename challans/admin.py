from django.contrib import admin
from .models import WeightEntry, Weight, Challan, ReportWeight


class WeightInline(admin.StackedInline):
    model = Weight
    extra = 0


class ChallanAdmin(admin.ModelAdmin):

    list_display = ("challan_no", "party", "total_amount", "created_on", "is_entries_done", "is_reports_done", "is_payed",  "status")
    list_filter = ("party", "created_on", "status")
    inlines = [WeightInline, ]
    list_editable = ("created_on", )


class WeightAdmin(admin.ModelAdmin):

    list_display = ("material", "rate_per_unit", "total_weight", "stock_weight", "challan")
    list_filter = ("challan", "material", "challan__created_on")


def get_challan_no(instance):
    return instance.weight.challan.challan_no


def get_material(instance):
    return instance.weight.material.name

# def get_weight(instance):
#     return instance.wei


class ReportWeightAdmin(admin.ModelAdmin):

    list_filter = ("weight__material", "weight__challan", "weight__challan__party")
    list_display = ("weight", get_challan_no, "weight_count", "report_type", "reported_on")


class WeightEntryAdmin(admin.ModelAdmin):

    list_display = ("entry", get_challan_no, get_material)
    list_filter = ("weight__material", "weight__challan")


admin.site.register(ReportWeight, ReportWeightAdmin)
admin.site.register(WeightEntry, WeightEntryAdmin)
admin.site.register(Weight, WeightAdmin)
admin.site.register(Challan, ChallanAdmin)
