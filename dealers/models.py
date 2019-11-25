from django.db import models


class Dealer(models.Model):

    name = models.CharField(max_length=128)
    dealer_code = models.CharField(max_length=32, blank=True)
    address = models.TextField(blank=True)
    business_name = models.CharField(max_length=256, blank=True)
    phone = models.CharField(max_length=13)
    whatsapp = models.CharField(max_length=13, blank=True)
    email = models.EmailField(blank=True, null=True)
    extra_info = models.TextField(blank=True)
    city = models.CharField(max_length=64, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def get_display_text(self):
        return self.name

