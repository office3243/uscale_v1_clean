from django.db import models


class PaymentParty(models.Model):

    name = models.CharField(max_length=128)
    is_self_firm = models.BooleanField(default=False)

    account_details = models.TextField(blank=True)

    def __str__(self):
        return self.name
