from django.contrib import admin
from .models import BankAccount


class BankAccountAdmin(admin.ModelAdmin):

    list_display = ("party", "acc_no", "ifsc_code", "bank_name", "branch_name")
    list_filter = ("party", "bank_name")


admin.site.register(BankAccount, BankAccountAdmin)
