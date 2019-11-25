from django.contrib import admin
from .models import Material


class MaterialAdmin(admin.ModelAdmin):

    list_display = ("material_code", "name", "attribute", "default_rate", "up_rate", "down_rate", "has_report")
    list_editable = ("default_rate", "up_rate", "down_rate")


admin.site.register(Material, MaterialAdmin)
