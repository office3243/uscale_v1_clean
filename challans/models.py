from django.urls import reverse_lazy
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from . import validators
from django.db.models import Sum, Count, Max, Min
from django.conf import settings
from django.db.models.signals import post_save, pre_save, m2m_changed, post_delete
import decimal
from rates.models import RateGroup, GroupMaterialRate
import math
from django.contrib.auth.models import User
from django.db.models import F
from django.core.exceptions import ValidationError


REPORT_PERCENT_LOWER = 10
REPORT_PERCENT_UPPER = 15


class WeightEntry(models.Model):

    weight = models.ForeignKey("Weight", on_delete=models.CASCADE)
    entry = models.FloatField(validators=[MinValueValidator(0.10), ],)

    def __str__(self):
        return str(self.entry)

    class Meta:
        verbose_name_plural = "Weight Entries"


def save_signal_to_parent(sender, instance, *args, **kwargs):
    """to send signal to parent model Weight on each save"""
    return instance.weight.save()


post_save.connect(save_signal_to_parent, sender=WeightEntry)
post_delete.connect(save_signal_to_parent, sender=WeightEntry)


class ReportWeight(models.Model):

    REPORT_TYPE_CHOICES = (("RP", "Report"), ("RT", "Return"))
    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    weight = models.OneToOneField("Weight", on_delete=models.CASCADE)
    weight_count = models.FloatField(default=0.0)
    report_type = models.CharField(max_length=2, choices=REPORT_TYPE_CHOICES)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    reported_on = models.DateTimeField(blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} - {} - {}".format(self.weight.material.name, self.weight_count, self.get_report_type_display())

    @property
    def get_stock_weight(self):
        if self.report_type == "RT":
            return self.weight_count
        return 0.00


def check_status_report_weight(sender, instance, *args, **kwargs):
    if (instance.weight_count > 0.00) and instance.status == "PN":
        instance.status = "DN"
        instance.save()
    elif not instance.weight_count and instance.status == "DN":
        instance.status = "PN"
        instance.save()


post_save.connect(save_signal_to_parent, sender=ReportWeight)
post_save.connect(check_status_report_weight, sender=ReportWeight)
post_delete.connect(save_signal_to_parent, sender=ReportWeight)


class Weight(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    challan = models.ForeignKey("Challan", on_delete=models.CASCADE)
    material = models.ForeignKey("materials.Material", on_delete=models.CASCADE)
    total_weight = models.FloatField(validators=[MinValueValidator(0.00)], default=0.00)
    rate_per_unit = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    updated_on = models.DateTimeField(auto_now=True)

    stock_weight = models.FloatField(validators=[MinValueValidator(0.00)], default=0.00)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    def __str__(self):
        return "{} * {} kg = {}".format(self.material.get_display_text, self.total_weight, self.amount)

    class Meta:
        unique_together = ("challan", "material")

    @property
    def calculate_total_weight(self):
        return round(self.calculate_weight_sum - self.get_report_weight, 2)

    @property
    def calculate_weight_sum(self):
        if self.weightentry_set.exists():
            return round(self.weightentry_set.aggregate(total_weight=Sum("entry"))['total_weight'], 2)
        return 0.00

    @property
    def get_report_weight(self):
        if hasattr(self, "reportweight"):
            return self.reportweight.weight_count
        else:
            return 0.0

    @property
    def get_report_stock_weight(self):
        if hasattr(self, "reportweight"):
            return self.reportweight.get_stock_weight
        else:
            return 0.0

    @property
    def calculate_stock_weight(self):
        return self.calculate_weight_sum - self.get_report_stock_weight

    @property
    def get_default_rate(self):
        if self.challan.party.rate_group:
            try:
                return GroupMaterialRate.objects.get(material=self.material, rate_group=self.challan.party.rate_group).amount
            except:
                pass
        return decimal.Decimal(self.material.default_rate)

    @property
    def get_report_weight_display(self):
        if hasattr(self, "reportweight"):
            return self.reportweight.weight_count
        else:
            return "-"

    @property
    def get_report_percent(self):
        try:
            return (self.reportweight.weight_count / self.calculate_weight_sum) * 100
        except:
            return 0

    @property
    def get_default_report_weight(self):
        return round(self.calculate_weight_sum * 0.1, 2)

    @property
    def get_last_report_percent(self):

        last_weights = Weight.objects.filter(challan__status="DN", challan__party=self.challan.party, material=self.material)
        if last_weights.exists():
            last_percent = last_weights.last().get_report_percent
            return last_percent
        else:
            return 0

    @property
    def get_report_reserve_percent(self):
        last_percent = self.get_last_report_percent
        return REPORT_PERCENT_LOWER if last_percent <= REPORT_PERCENT_LOWER else REPORT_PERCENT_UPPER

    @property
    def calculate_weight_amount(self):
        if self.rate_per_unit:
            return self.rate_per_unit * decimal.Decimal(self.total_weight)
        return decimal.Decimal(0.00)

    @property
    def calculate_amount(self):
        weight_amount = self.calculate_weight_amount
        if hasattr(self, "reportweight") and self.reportweight.status == "PN":
            amount = self.calculate_weight_amount * decimal.Decimal(1-(self.get_report_reserve_percent/100))
        else:
            amount = weight_amount
        return amount

    @property
    def get_recent_entry(self):
        return self.weightentry_set.last() or None

    def refresh_challan(self):
        self.challan.save()

    def clean(self):
        if not self.material.check_allowed_rate(self.rate_per_unit):
            raise ValidationError("Rate must be between {} and {}".format(self.material.down_rate, self.material.up_rate))


def assign_rate_per_unit(sender, instance, *args, **kwargs):
    if not instance.rate_per_unit:
        instance.rate_per_unit = instance.get_default_rate
        instance.save()


def assign_total_weight(sender, instance, *args, **kwargs):
    total_weight = instance.calculate_total_weight
    if instance.total_weight != total_weight:
        instance.total_weight = total_weight
        instance.save()


def assign_amount(sender, instance, *args, **kwargs):
    amount = instance.calculate_amount
    if instance.amount != amount:
        instance.amount = amount
        instance.save()


def check_weight_status(sender, instance, *args, **kwargs):
    if hasattr(instance, "reportweight"):
        report_done = (instance.reportweight.status == "DN")
        if report_done and instance.status == "PN":
            instance.status = "DN"
            instance.save()
        elif not report_done and instance.status == "DN":
            instance.status = "PN"
            instance.save()
    elif instance.status == "PN":
        instance.status = "DN"
        instance.save()


def refresh_challan(sender, instance, *args, **kwargs):
    instance.refresh_challan()


def assign_stock_weight(sender, instance, *args, **kwargs):
    stock_weight = instance.calculate_stock_weight
    if instance.stock_weight != stock_weight:
        instance.stock_weight = stock_weight
        instance.save()


post_save.connect(assign_rate_per_unit, sender=Weight)
post_save.connect(assign_total_weight, sender=Weight)
post_save.connect(assign_amount, sender=Weight)
post_save.connect(check_weight_status, sender=Weight)
post_save.connect(refresh_challan, sender=Weight)
post_save.connect(assign_stock_weight, sender=Weight)
post_delete.connect(refresh_challan, sender=Weight)


class Challan(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    party = models.ForeignKey("parties.Party", on_delete=models.CASCADE)
    challan_no = models.PositiveIntegerField(blank=True, null=True)
    vehicle_details = models.CharField(max_length=128, blank=True, null=True)
    weights_amount = models.DecimalField(max_digits=9, decimal_places=2, default=decimal.Decimal(0.00))
    extra_charges = models.DecimalField(verbose_name="Kata Charges", max_digits=9, decimal_places=2,
                                        default=decimal.Decimal(0.00), validators=[MinValueValidator(limit_value=0), MaxValueValidator(limit_value=100)])
    round_amount = models.DecimalField(max_digits=4, decimal_places=2, default=decimal.Decimal(0.00), validators=[MinValueValidator(limit_value=-10), MaxValueValidator(limit_value=10)])
    total_amount = models.DecimalField(max_digits=9, decimal_places=2, default=decimal.Decimal(0.00), validators=[MinValueValidator(limit_value=0)])
    image = models.ImageField(upload_to="payments/", blank=True, null=True)
    extra_info = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=True)
    updated_on = models.DateTimeField(auto_now=True, editable=True)

    is_entries_done = models.BooleanField(default=False)
    is_reports_done = models.BooleanField(default=False)
    is_rates_assigned = models.BooleanField(default=False)
    is_payed = models.BooleanField(default=False)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    def __str__(self):
        return str(self.challan_no)

    @property
    def get_high_report_reserve_weights(self):
        report_reserve_weights = []
        for weight in self.weight_set.all():
            if weight.get_last_report_percent > REPORT_PERCENT_LOWER and weight.status == "PN":
                report_reserve_weights.append(weight)
        return report_reserve_weights

    @property
    def get_date_display(self):
        return self.created_on.strftime("%d/%m/%y")

    @property
    def get_paying_amount(self):
        return self.total_amount

    @property
    def get_display_text(self):
        return self.challan_no

    @property
    def get_challan_has_report(self):
        return self.weight_set.filter(material__has_report=True).exists()

    @property
    def get_materials_has_report(self):
        return self.weight_set.filter(material__has_report=True)

    @property
    def calculate_weights_amount(self):
        if self.weight_set.exists():
            return decimal.Decimal(math.ceil(self.weight_set.aggregate(amount=Sum("amount"))['amount']))
        else:
            return decimal.Decimal(0.00)

    @property
    def get_absolute_url(self):
        return reverse_lazy("challans:detail", kwargs={"challan_no": self.challan_no})

    @property
    def get_entries_url(self):
        return reverse_lazy("challans:entries", kwargs={'challan_no': self.challan_no})

    @property
    def get_assign_reports_url(self):
        return reverse_lazy("challans:assign_reports", kwargs={'challan_no': self.challan_no})

    @property
    def get_entries_submit_url(self):
        return reverse_lazy("challans:entries_submit", kwargs={"challan_no": self.challan_no})

    @property
    def get_assign_rates_url(self):
        return reverse_lazy("challans:assign_rates", kwargs={'challan_no': self.challan_no})

    @property
    def get_update_url(self):
        return reverse_lazy("challans:update", kwargs={"challan_no": self.challan_no})

    @property
    def get_payment_add_url(self):
        return reverse_lazy("payments:add", kwargs={"challan_no": self.challan_no})

    @property
    def get_done_url(self):
        return reverse_lazy("challans:done", kwargs={"challan_no": self.challan_no})

    @property
    def get_recent_weight_entry(self):
        return self.weight_set.latest("updated_on").get_recent_entry or None

    @property
    def get_payable_amount(self):
        return self.total_amount

    def refresh_weights(self):
        for weight in self.weight_set.all():
            weight.save()

    @property
    def calculate_total_amount(self):
        return self.weights_amount - self.extra_charges + self.round_amount


def check_status(sender, instance, *args, **kwargs):
    all_done = all([instance.is_entries_done, instance.is_payed, instance.is_reports_done])
    if all_done and instance.status == "PN":
        instance.status = "DN"
        instance.save()
    if not all_done and instance.status == "DN":
        instance.status = "PN"
        instance.save()


def check_reports_done(sender, instance, *agrs, **kwargs):
    if instance.weight_set.filter(status="PN").exists() and instance.is_reports_done:
        instance.is_reports_done = False
        instance.save()
    elif not instance.weight_set.filter(status="PN").exists() and not instance.is_reports_done:
        instance.is_reports_done = True
        instance.save()


def check_is_payed(sender, instance, *agrs, **kwargs):
    if hasattr(instance, "payment"):
        if instance.payment.amount != instance.total_amount:
            instance.payment.amount = instance.total_amount
            instance.save()
        if instance.payment.status == "DN" and not instance.is_payed:
            instance.is_payed = True
            instance.save()
        elif instance.payment.status == "PN" and instance.is_payed:
            instance.is_payed = False
            instance.save()


def assign_weights_amount(sender, instance, *args, **kwargs):
    weights_amount = instance.calculate_weights_amount
    if instance.weights_amount != weights_amount:
        instance.weights_amount = weights_amount
        instance.save()


def assign_total_amount(sender, instance, *args, **kwargs):
    total_amount = instance.calculate_total_amount
    if instance.total_amount != total_amount:
        instance.total_amount = total_amount
        instance.save()


def challan_no_generator(challan):
    return challan.id


def assign_challan_no(sender, instance, *args, **kwargs):
    if not instance.challan_no:
        """temporary for testing"""
        challan_no = challan_no_generator(instance)
        if instance.challan_no != challan_no:
            instance.challan_no = challan_no
            instance.save()


post_save.connect(assign_challan_no, sender=Challan)
post_save.connect(assign_weights_amount, sender=Challan)
post_save.connect(assign_total_amount, sender=Challan)
post_save.connect(check_reports_done, sender=Challan)
post_save.connect(check_is_payed, sender=Challan)
post_save.connect(check_status, sender=Challan)
