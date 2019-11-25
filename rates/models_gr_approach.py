from django.db import models


class RateGroup(models.Model):

    name = models.CharField(max_length=64)
    extra_info = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def get_display_text(self):
        return self.name


class GroupRate(models.Model):

    rate_group = models.ForeignKey(RateGroup, on_delete=models.CASCADE)

    material = models.ForeignKey("materials.Material", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)

    extra_info = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.amount) + self.material.get_display_text + self.rate_group.get_display_text

    @property
    def get_display_text(self):
        return str(self.amount)

    class Meta:
        unique_together = ("material", "rate_group")


class IndividualRate(models.Model):

    parties = models.ManyToManyField("parties.Party")

    material = models.ForeignKey("materials.Material", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)

    extra_info = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.amount) + self.material.get_display_text

    @property
    def get_display_text(self):
        return str(self.amount)
