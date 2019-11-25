from django.db import models
from django.utils import timezone
from challans.models import Challan, Weight
from django.db.models import Min, Max, Sum, Q
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from loadings.models import Loading, LoadingWeight
from django.contrib import messages
from materials.models import Material


def get_start_date():
    today = timezone.now().date()
    try:
        challan_date = Challan.objects.aggregate(min_date=Min("created_on"))['min_date'].date()
    except:
        challan_date = today
    try:
        loading_date = Loading.objects.aggregate(min_date=Min("created_on__date"))['min_date'].date()
    except:
        loading_date = today
    return min(challan_date, loading_date)


class MaterialStock(models.Model):

    STATUS_CHOICES = (("PN", "Pending"), ("DN", "Done"))

    date = models.DateField(auto_created=True)
    updated_on = models.DateTimeField(auto_now=True)

    material = models.ForeignKey("materials.Material", on_delete=models.PROTECT)
    opening_weight = models.FloatField(default=0.0)
    in_weight = models.FloatField(default=0.0)
    merge_in_weight = models.FloatField(default=0.0)
    out_weight = models.FloatField(default=0.0)
    closing_weight = models.FloatField(default=0.0)

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PN")

    def __str__(self):
        return "{} - {} {}".format(self.date, self.material.get_display_text, self.opening_weight)

    class Meta:
        ordering = ("-date", )

    @property
    def is_first_stock(self):
        if self.date <= get_start_date():
            return True
        return False

    @property
    def is_last_stock(self):
        if self.date >= timezone.now().date():
            return True
        return False

    @property
    def get_previous_stock(self):
        if self.is_first_stock:
            return None
        previous_stock = MaterialStock.objects.get_or_create(date=self.date-timezone.timedelta(days=1), material=self.material)[0]
        # previous_stock.save()
        return previous_stock

    @property
    def get_next_stock(self):
        if self.is_last_stock:
            return None
        next_stock = MaterialStock.objects.get_or_create(date=self.date+timezone.timedelta(days=1), material=self.material)[0]
        # previous_stock.save()
        return next_stock

    @property
    def calculate_opening_weight(self):
        previous_stock = self.get_previous_stock
        if previous_stock is not None:
            return previous_stock.closing_weight
        return 0.00

    #   Challans Section

    @property
    def get_in_weight_display(self):
        if self.material.get_merge_materials.exists():
            return "{} + {} = {}".format(self.in_weight-self.merge_in_weight, self.merge_in_weight, self.in_weight)
        else:
            return self.in_weight

    @property
    def get_challans(self):
        return Challan.objects.filter(created_on__date=self.date)

    @property
    def calcualte_challans_weight(self):
        challans_weight = Weight.objects.filter(challan__in=self.get_challans, material=self.material).aggregate(total=Sum("stock_weight"))['total'] or 0.00
        return round(challans_weight, 2)

    @property
    def calculate_in_weight(self):
        in_weight = self.calcualte_challans_weight + self.calculate_merge_in_weight
        return round(in_weight, 2)

    @property
    def calculate_merge_in_weight(self):
        merge_weight = 0
        if self.material.get_merge_materials.exists():
            for material in self.material.get_merge_materials:
                merge_weight += (Weight.objects.filter(challan__in=self.get_challans, material=material).aggregate(total=Sum("stock_weight"))['total'] or 0.00)
        return merge_weight

    @property
    def check_challan_status(self):
        return not self.get_challans.filter(is_reports_done=False).exists()

    #   Loadings

    @property
    def get_loadings(self):
        return Loading.objects.filter(created_on__date=self.date)

    @property
    def calculate_out_weight(self):
        out_weight = LoadingWeight.objects.filter(loading__in=self.get_loadings, material=self.material).aggregate(total=Sum("weight_count"))['total'] or 0.00
        return round(out_weight, 2)

    @property
    def check_loading_status(self):
        return not self.get_loadings.exclude(status="DN").exists()

    #   ---------------------

    @property
    def check_previous_status(self):
        previous_stock = self.get_previous_stock
        if previous_stock is not None:
            return previous_stock.status == "DN"
        return True

    @property
    def calculate_closing_weight(self):
        return round((self.opening_weight + self.in_weight - self.out_weight), 2)

    @property
    def check_status(self):
        return "DN" if (self.check_challan_status and self.check_previous_status and self.check_loading_status) else "PN"


# def check_merge_material(sender, created, instance, *args, **kwargs):
#     if created:
#         if instance.material.get_merge_material:
#             instance.delete()


def assign_opening_weight(sender, instance, *args, **kwargs):
    if not instance.is_first_stock:
        opening_weight = instance.calculate_opening_weight
        if instance.opening_weight != opening_weight:
            instance.opening_weight = opening_weight
            instance.save()


def assign_merge_in_weight(sender, instance, *args, **kwargs):
    merge_in_weight = instance.calculate_merge_in_weight
    if instance.merge_in_weight != merge_in_weight:
        instance.merge_in_weight = merge_in_weight
        instance.save()


def assign_in_weight(sender, instance, *args, **kwargs):
    in_weight = instance.calculate_in_weight
    if instance.in_weight != in_weight:
        instance.in_weight = in_weight
        instance.save()


def assign_out_weight(sender, instance, *args, **kwargs):
    out_weight = instance.calculate_out_weight
    if instance.out_weight != out_weight:
        instance.out_weight = out_weight
        instance.save()


def assign_closing_weight(sender, instance, *args, **kwargs):
    closing_weight = instance.calculate_closing_weight
    if instance.closing_weight != closing_weight:
        instance.closing_weight = closing_weight
        instance.save()


def assign_status(sender, instance, *args, **kwargs):
    status = instance.check_status
    if instance.status != status:
        instance.status = status
        instance.save()


def refresh_next_stock(sender, instance, *args, **kwargs):
    if instance.get_next_stock:
        return instance.get_next_stock.save()


def assign_all_changes(sender, instance, *args, **kwargs):

    is_changed = False

    if not instance.is_first_stock:
        opening_weight = instance.calculate_opening_weight
        if instance.opening_weight != opening_weight:
            instance.opening_weight = opening_weight
            is_changed = True

    merge_in_weight = instance.calculate_merge_in_weight
    if instance.merge_in_weight != merge_in_weight:
        instance.merge_in_weight = merge_in_weight
        is_changed = True

    in_weight = instance.calculate_in_weight
    if instance.in_weight != in_weight:
        instance.in_weight = in_weight
        is_changed = True

    out_weight = instance.calculate_out_weight
    if instance.out_weight != out_weight:
        instance.out_weight = out_weight
        is_changed = True

    closing_weight = instance.calculate_closing_weight
    if instance.closing_weight != closing_weight:
        instance.closing_weight = closing_weight
        is_changed = True

    status = instance.check_status
    if instance.status != status:
        instance.status = status
        is_changed = True

    if is_changed:
        instance.save()

# post_save.connect(check_merge_material, sender=MaterialStock)
post_save.connect(assign_all_changes, sender=MaterialStock)
# post_save.connect(assign_opening_weight, sender=MaterialStock)
# post_save.connect(assign_merge_in_weight, sender=MaterialStock)
# post_save.connect(assign_in_weight, sender=MaterialStock)
# post_save.connect(assign_out_weight, sender=MaterialStock)
# post_save.connect(assign_closing_weight, sender=MaterialStock)
# post_save.connect(assign_status, sender=MaterialStock)
post_save.connect(refresh_next_stock, sender=MaterialStock)


def create_todays_stocks():
    for material in Material.objects.filter(merge_material=None).all():
        MaterialStock.objects.get_or_create(material=material, date=timezone.now().date())
