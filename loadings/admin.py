from django.contrib import admin
from .models import Loading, LoadingWeight


class LoadingAdmin(admin.ModelAdmin):

    list_display = ("dealer", "created_on")
    readonly_fields = ("updated_on", )
    list_editable = ("created_on", )


admin.site.register(LoadingWeight)
admin.site.register(Loading, LoadingAdmin)
