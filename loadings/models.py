from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse_lazy
from django.db.models.signals import pre_save, post_save


class Loading(models.Model):

    STATUS_CHOICES = (("CR", "Created"), ("ED", "Entries Done"), ("DN", "DN"))

    loading_no = models.CharField(max_length=12, unique=True)
    dealer = models.ForeignKey("dealers.Dealer", on_delete=models.PROTECT)
    vehicle_details = models.TextField(blank=True)
    extra_info = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="CR")

    def __str__(self):
        return "{} - {}".format(self.loading_no, self.dealer.get_display_text)

    @property
    def get_display_text(self):
        return self.__str__()

    @property
    def get_entries_url(self):
        return reverse_lazy("loadings:entries", kwargs={"id": self.id})

    @property
    def get_absolute_url(self):
        return reverse_lazy("loadings:detail", kwargs={"id": self.id})


def assign_loading_no(sender, instance, *args, **kwargs):
    if not instance.loading_no:
        instance.loading_no = instance.id
        instance.save()


post_save.connect(assign_loading_no, Loading)


class LoadingWeight(models.Model):

    loading = models.ForeignKey(Loading, on_delete=models.CASCADE)
    material = models.ForeignKey("materials.Material", on_delete=models.PROTECT)
    weight_count = models.FloatField(validators=[MinValueValidator(limit_value=1.0)])

    def __str__(self):
        return "{} - {} {}".format(self.loading.get_display_text, self.material.get_display_text, self.weight_count)

    class Meta:
        unique_together = ("material", "loading")
