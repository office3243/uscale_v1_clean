from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator
from decimal import Decimal
from django.db.models import Sum


class BankAccount(models.Model):
    party = models.ForeignKey("parties.Party", on_delete=models.CASCADE)
    amount_limit = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal(1000000), editable=False)
    account_holder = models.CharField(max_length=128)
    acc_no = models.CharField(max_length=32)
    ifsc_code = models.CharField(max_length=11, validators=[MinLengthValidator(limit_value=11)])
    bank_name = models.CharField(max_length=64)
    branch_name = models.CharField(max_length=64, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {} - {}".format(self.party.name, self.bank_name, self.acc_no[-5:])

    @property
    def get_display_text(self):
        return "{} - {} - {}".format(self.account_holder, self.bank_name, self.acc_no[-5:])

    @property
    def get_tr_amount(self):
        return self.accounttransaction_set.aggregate(total=Sum("amount"))['total']
