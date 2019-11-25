from django.db import models
from django.db.models.signals import post_save, post_delete, pre_delete
from django.db.models import Sum, Max, Count
from django.core.validators import ValidationError
from decimal import Decimal
from itertools import chain
from operator import attrgetter
from django.conf import settings
from django.urls import reverse_lazy
from parties.models import WalletAdvance
from django.utils import timezone


def save_payment(sender, instance, *args, **kwargs):
    instance.payment.save()


class InPayment(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))
    GATEWAY_CHOICES = (("AD", "Adjusted"), ("WL", "Wallet"), ("CS", "Cash"))

    gateway = models.CharField(max_length=2, choices=GATEWAY_CHOICES)

    wallet_advance = models.OneToOneField("parties.WalletAdvance", on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    created_on = models.DateField(default=timezone.now)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="DN")

    def __str__(self):
        return str(self.amount)


def create_wallet_advance(sender, instance, created, *args, **kwargs):
    if created and instance.gateway == "WL":
        wallet_advance = WalletAdvance.objects.create(amount=instance.amount, wallet=instance.payment.challan.party.get_wallet, gateway="WL")
        instance.wallet_advance = wallet_advance
        instance.save()


def refund_wallet_advance(sender, instance, *args, **kwargs):
    if instance.gateway == "WL":
        instance.wallet_advance.refund_amount_and_delete()


post_save.connect(create_wallet_advance, sender=InPayment)
post_save.connect(save_payment, sender=InPayment)
post_delete.connect(save_payment, sender=InPayment)
post_delete.connect(refund_wallet_advance, sender=InPayment)


class AccountTransaction(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    payment_code = models.CharField(max_length=32, blank=True, null=True)
    payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
    actr_no = models.CharField(verbose_name="Payment No", max_length=7, default=settings.ACTR_NO_PREFIX)
    serial_no = models.CharField(verbose_name="PY Serial No", max_length=7, blank=tuple, null=True)
    bank_account = models.ForeignKey("bank_accounts.BankAccount", on_delete=models.CASCADE, blank=True, null=True)
    payment_party = models.ForeignKey("payment_parties.PaymentParty", on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created_on = models.DateField(default=timezone.now)
    payed_on = models.DateField(default=timezone.now)
    extra_info = models.TextField(blank=True)
    photo = models.ImageField(upload_to="payments/account_transactions/photos/", blank=True, null=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    def __str__(self):
        return str(self.amount)

    def get_admin_absolute_url(self):
        return reverse_lazy("cms_admin:account_transactions_detail", kwargs={"id": self.id})

    def get_admin_update_url(self):
        return reverse_lazy("cms_admin:account_transactions_update", kwargs={"id": self.id})


def generate_ac_tr_payment_code(ac_tr):
    return "{}-{}".format(settings.BRANCH_AC_PAYMENT_PREFIX, ac_tr.id)


def assign_ac_tr_payment_code(sender, instance, *args, **kwargs):
    payment_code = generate_ac_tr_payment_code(instance)
    if instance.payment_code != payment_code:
        instance.payment_code = payment_code
        instance.save()

# def assign_payed_on(sender, instance, *args, **kwargs):


def check_status_ac_tr(sender, instance, *args, **kwargs):
    if not (instance.payment_party and instance.payed_on) and instance.status == "DN":
        instance.status = "PN"
        instance.save()
    elif (instance.payment_party and instance.payed_on) and instance.status == "PN":
        instance.status = "DN"
        instance.save()


post_save.connect(check_status_ac_tr, sender=AccountTransaction)
post_save.connect(assign_ac_tr_payment_code, sender=AccountTransaction)
post_save.connect(save_payment, sender=AccountTransaction)
post_delete.connect(save_payment, sender=AccountTransaction)


class CashTransaction(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    created_on = models.DateField(default=timezone.now)
    payed_on = models.DateTimeField(blank=True, null=True)
    extra_info = models.TextField(blank=True)
    photo = models.ImageField(upload_to="payments/account_transactions/photos/", blank=True, null=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="DN")

    def __str__(self):
        return str(self.amount)


post_save.connect(save_payment, sender=CashTransaction)
post_delete.connect(save_payment, sender=CashTransaction)


class WalletTransaction(models.Model):

    payment = models.ForeignKey("Payment", on_delete=models.CASCADE)
    wallet = models.ForeignKey("parties.Wallet", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal(0.00))
    created_on = models.DateField(default=timezone.now)
    deducted_amount = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal(0.00))

    previous_balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def refund_amount(self):
        self.wallet.add_balance(amount=self.amount)

    def deduct_from_wallet(self, amount):
        self.previous_balance = self.wallet.balance
        self.wallet.deduct_balance(amount)
        self.deducted_amount += amount
        self.save()

    def update_amount(self, new_amount):
        self.amount += new_amount
        self.save()

    def __str__(self):
        return str(self.amount)


def deduct_from_wallet(sender, instance, *args, **kwargs):
    if instance.deducted_amount != instance.amount:
        instance.deduct_from_wallet(instance.amount-instance.deducted_amount)


def refund_to_wallet(sender, instance, *args, **kwargs):
    instance.wallet.add_balance(instance.amount)


def assign_previous_balance(sender, created, instance, *args, **kwargs):
    if created:
        previous_balance = instance.wallet.balance
        if instance.previous_balance != previous_balance:
            instance.previous_balance = previous_balance
            instance.save()


post_save.connect(assign_previous_balance, sender=WalletTransaction)
post_save.connect(deduct_from_wallet, sender=WalletTransaction)
post_save.connect(save_payment, sender=WalletTransaction)
post_delete.connect(refund_to_wallet, sender=WalletTransaction)
post_delete.connect(save_payment, sender=WalletTransaction)


class Payment(models.Model):
    PAYMENT_MODE_CHOICES = (("DP", "Direct Payment"), ("AL", "Account Less"))
    PAYMENT_STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    challan = models.OneToOneField("challans.Challan", on_delete=models.CASCADE)
    payment_mode = models.CharField(max_length=2, choices=PAYMENT_MODE_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=2, choices=PAYMENT_STATUS_CHOICES, default="PN")
    payed_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    payed_on = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to="payments/", blank=True, null=True)
    extra_info = models.TextField(blank=True)
    created_on = models.DateField(default=timezone.now)

    def __str__(self):
        return "{} - {} ({}) - ".format(self.challan.party.get_display_text, self.amount, self.get_status_display())

    @property
    def get_date_display(self):
        return self.created_on.strftime("%d/%m/%Y")

    @property
    def calculate_payed_amount(self):
        print(sum([self.get_ac_tr_amount, self.get_cash_tr_amount, self.get_wallet_tr_amount, -self.get_inpayment_amount]))
        return sum([self.get_ac_tr_amount, self.get_cash_tr_amount, self.get_wallet_tr_amount, -self.get_inpayment_amount])

    @property
    def get_absolute_url(self):
        return reverse_lazy("payments:detail", kwargs={"id": self.id})

    @property
    def get_admin_absolute_url(self):
        return reverse_lazy("cms_admin:payments_detail", kwargs={"id": self.id})

    @property
    def get_inpayment_amount(self):
        if self.inpayment_set.exists():
            print(self.inpayment_set.first().amount)
            return self.inpayment_set.first().amount
        else:
            print("ELES")
            return Decimal(0.00)

    @property
    def calculate_payed_amount_pending(self):
        return sum([self.get_ac_tr_amount_pending, ])

    @property
    def calculate_payed_amount_succeed(self):
        return sum([self.get_ac_tr_amount_succeed, self.get_cash_tr_amount, self.get_wallet_tr_amount, -self.get_inpayment_amount])

    @property
    def get_remaining_amount(self):
        return self.amount - self.payed_amount

    @property
    def get_is_wallet_payed(self):
        return self.wallettransaction_set.exists()

    @property
    def get_amount_payed_succeed(self):
        return self

    @property
    def get_wallet_tr_amount(self):
        return self.wallettransaction_set.aggregate(total=Sum("amount"))["total"] or Decimal(0.00)

    @property
    def get_cash_tr_amount(self):
        return self.cashtransaction_set.aggregate(total=Sum("amount"))["total"] or Decimal(0.00)

    @property
    def get_ac_tr_amount(self):
        return self.accounttransaction_set.aggregate(total=Sum("amount"))["total"] or Decimal(0.00)

    @property
    def get_ac_tr_amount_succeed(self):
        return self.accounttransaction_set.filter(status="DN").aggregate(total=Sum("amount"))["total"] or Decimal(0.00)

    @property
    def get_ac_tr_amount_pending(self):
        return self.accounttransaction_set.filter(status="PN").aggregate(total=Sum("amount"))["total"] or Decimal(0.00)

    def validate_amounts(self):
        """validate all transaction amounts with total"""
        transactions_sum = self.calculate_payed_amount
        if transactions_sum > self.amount:
            raise ValidationError("Paying amount cannot be greater than Actual amount")

    # def clean(self):
    #     super().clean()
    #     self.validate_amounts()


def assign_payment_mode(sender, instance, *args, **kwargs):
    if instance.status == "PN":
        payment_mode = "AL" if instance.challan.party.wallet_set.filter(is_active=True).exists() else "DP"
        if instance.payment_mode != payment_mode:
            instance.payment_mode = payment_mode
            instance.save()


def assign_amount(sender, instance, *args, **kwargs):
    challan_amount = instance.challan.get_paying_amount
    if instance.amount != challan_amount:
        instance.amount = challan_amount
        instance.save()


def assign_payed_amount(sender, instance, *args, **kwargs):
    payed_amount = instance.calculate_payed_amount
    print(payed_amount)
    if instance.payed_amount != payed_amount:
        instance.payed_amount = payed_amount
        instance.save()


def check_payment_status(sender, instance, *args, **kwargs):
    ac_tr_pending = instance.accounttransaction_set.filter(status="PN").exists()

    if (instance.amount != instance.payed_amount or ac_tr_pending or not instance.challan.is_reports_done) and instance.status == "DN":
        instance.status = "PN"
        print(5)
        instance.save()
    elif instance.amount == instance.payed_amount and instance.status == "PN" and instance.challan.is_reports_done and not ac_tr_pending:
        print(6)
        instance.status = "DN"
        instance.save()


def refresh_challan(sender, instance, *args, **kwargs):
    instance.challan.save()


def clean_payment(sender, instance, *agrs, **kwargs):
    print("Full Clean")
    instance.full_clean()



post_save.connect(assign_payment_mode, sender=Payment)
post_save.connect(assign_amount, sender=Payment)
post_save.connect(clean_payment, sender=Payment)
post_save.connect(assign_payed_amount, sender=Payment)
post_save.connect(check_payment_status, sender=Payment)
post_save.connect(refresh_challan, sender=Payment)
