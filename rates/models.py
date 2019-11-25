from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy


class RateGroup(models.Model):

    name = models.CharField(max_length=64)
    extra_info = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def get_display_text(self):
        return self.name

    @property
    def get_active_parties(self):
        return self.party_set.filter(is_active=True)

    @property
    def get_non_active_parties(self):
        return self.party_set.filter(is_active=False)

    @property
    def get_absolute_url(self):
        return reverse_lazy("rates:rate_group_detail", kwargs={"id": self.id})

    @property
    def get_update_url(self):
        return reverse_lazy("rates:rate_group_update", kwargs={"id": self.id})


class GroupMaterialRate(models.Model):

    material = models.ForeignKey("materials.Material", on_delete=models.CASCADE)
    rate_group = models.ForeignKey(RateGroup, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=9, decimal_places=2)
    extra_info = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_on = models.DateTimeField(auto_now=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {} (Group {}({})".format(self.material.get_display_text, self.amount,
                                              self.rate_group.get_display_text,
                                              self.rate_group.party_set.count()
                                              )

    @property
    def get_update_url(self):
        return reverse_lazy("rates:material_rate_update", kwargs={"id": self.id})

    def clean(self):
        super().clean()
        if not self.material.check_allowed_rate(self.amount):
            raise ValidationError("Rate must be between {} and {}".format(self.material.down_rate, self.material.up_rate))

    class Meta:
        unique_together = ("material", "rate_group")
        verbose_name = "Grouped Material Rate"
        verbose_name_plural = "Grouped Material Rates"
