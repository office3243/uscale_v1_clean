from django.db import models
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator


class Material(models.Model):
    name = models.CharField(max_length=64)
    attribute = models.CharField(max_length=6, blank=True)
    material_code = models.CharField(max_length=12)
    extra_info = models.TextField(blank=True)
    has_report = models.BooleanField(default=False)
    merge_material = models.ForeignKey("self", related_name="merge_materials", on_delete=models.SET_NULL, blank=True, null=True)

    up_rate = models.FloatField(default=1.0, validators=[MinValueValidator(limit_value=0.1)])
    default_rate = models.FloatField(default=1.0, validators=[MinValueValidator(limit_value=0.1)])
    down_rate = models.FloatField(default=1.0, validators=[MinValueValidator(limit_value=0.1)])

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def get_display_text(self):
        return self.name

    @property
    def get_absolute_url(self):
        return reverse_lazy("materials:detail", kwargs={"material_code": self.material_code})

    def check_allowed_rate(self, amount):
        if amount < self.down_rate or amount > self.up_rate:
            return False
        return True

    @property
    def get_merge_material(self):
        return self.merge_material

    @property
    def get_merge_materials(self):
        return self.merge_materials.all()
