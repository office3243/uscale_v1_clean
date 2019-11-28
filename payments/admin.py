from django.contrib import admin
from .models import AccountTransaction, Payment, WalletTransaction, CashTransaction, InPayment


admin.site.register(InPayment)


class PaymentAdmin(admin.ModelAdmin):

    list_display = ("challan", "payment_mode", "amount", "payed_amount", "status")
    list_display_links = ("challan", )
    list_filter = ("payment_mode", "challan__party", "status", "challan__created_on")


admin.site.register(Payment, PaymentAdmin)


class AccountTransactionAdmin(admin.ModelAdmin):

    list_display = ("amount", "actr_no", "bank_account", "status", "payed_on")
    list_filter = ("payment__challan__party", "status", "payed_on")
    list_editable = ("payed_on", )


admin.site.register(AccountTransaction, AccountTransactionAdmin)


class CashTransactionAdmin(admin.ModelAdmin):

    list_display = ("amount", "status", "payed_on", )
    list_filter = ("payment__challan__party", "status", "payed_on")
    list_editable = ("payed_on", )


admin.site.register(CashTransaction, CashTransactionAdmin)


class WalletTransactionAdmin(admin.ModelAdmin):

    list_display = ("amount", "payed_on")
    list_filter = ("wallet__deduct_type", "payment__challan__party", "payed_on")
    list_editable = ("payed_on", )


admin.site.register(WalletTransaction, WalletTransactionAdmin)

