from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from challans.models import Challan
from .models import Payment, AccountTransaction, CashTransaction, WalletTransaction
from django.utils import timezone
import decimal
from bank_accounts.models import BankAccount
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

#
# @login_required
# def add(request, challan_no):
#     challan = get_object_or_404(Challan, challan_no=challan_no, is_entries_done=True)
#     if challan.is_payed:
#         messages.warning(request, "Challan is already paid")
#         return redirect(challan.get_absolute_url)
#     if not challan.is_rates_assigned:
#         return redirect(challan.get_assign_rates_url)
#     challan.save()
#     party = challan.party
#     wallet = party.get_wallet
#     print(wallet)
#     payment = Payment.objects.get_or_create(challan=challan)[0]
#     payment.save()
#     if request.method == "POST":
#         print(request.POST)
#         extra_charges = decimal.Decimal(request.POST.get('extra_charges') or 0)
#         round_amount = decimal.Decimal(request.POST.get('round_amount') or 0)
#         print(extra_charges, round_amount)
#         if extra_charges or round_amount:
#             if extra_charges:
#                 challan.extra_charges = extra_charges
#             if round_amount:
#                 print("round True")
#                 challan.round_amount = round_amount
#             challan.save()
#         print(challan.round_amount, challan.extra_charges)
#         cash_amount = decimal.Decimal(request.POST.get('cash_amount') or 0)
#         account_amount_1 = decimal.Decimal(request.POST.get('account_amount') or 0)
#         ac_less_amount = decimal.Decimal(request.POST.get('ac_less_amount') or 0)
#         total_pay = cash_amount + account_amount_1 + ac_less_amount + payment.payed_amount + round_amount - extra_charges
#         if total_pay > payment.amount:
#             messages.warning(request, "Amount should be less or equal to {}".format(payment.amount))
#             return redirect(challan.get_payment_add_url)
#         if cash_amount:
#             cash_transaction = CashTransaction.objects.create(payment=payment, amount=cash_amount, payed_on=timezone.now(), status="DN")
#         if account_amount_1:
#             bank_account_id_1 = (request.POST.get('bank_account') or None)
#             bank_account_1 = get_object_or_404(BankAccount, id=bank_account_id_1, party=party)
#             account_transaction_1 = AccountTransaction.objects.create(payment=payment, amount=account_amount_1,
#                                                                       bank_account=bank_account_1)
#         if wallet is not None and ac_less_amount:
#             wallet_transaction, created = WalletTransaction.objects.get_or_create(payment=payment, wallet=wallet)
#             print(created, "--------------------------------------")
#             if created:
#                 wallet_transaction.amount = ac_less_amount
#                 wallet_transaction.deduct_from_wallet(ac_less_amount)
#                 wallet_transaction.save()
#             else:
#                 print("ELSE")
#                 wallet_transaction.update_amount(ac_less_amount)
#                 print(wallet_transaction.amount)
#                 wallet_transaction.save()
#         payment.save()
#         return redirect(challan.get_absolute_url)
#     else:
#         context = {"challan": challan, "payment": payment}
#         if payment.payment_mode == "AL":
#             context['wallet'] = wallet
#             context['wallet_payable_amount'], context['non_wallet_amount'] = wallet.get_payable_amount(payment.get_remaining_amount)
#             print(context)
#         return render(request, "payments/add.html", context)


@login_required
def add(request, challan_no):
    challan = get_object_or_404(Challan, challan_no=challan_no, is_entries_done=True)
    if challan.is_payed:
        messages.warning(request, "Challan is already paid")
        return redirect(challan.get_absolute_url)
    if not challan.is_rates_assigned:
        return redirect(challan.get_assign_rates_url)
    challan.save()
    party = challan.party
    wallet = party.get_wallet
    print(wallet)
    payment = Payment.objects.get_or_create(challan=challan)[0]
    payment.save()
    challan = payment.challan
    if request.method == "POST":
        print(request.POST)
        extra_charges = decimal.Decimal(request.POST.get('extra_charges') or 0)
        round_amount = decimal.Decimal(request.POST.get('round_amount') or 0)
        print(extra_charges, round_amount)
        if extra_charges or round_amount:
            if extra_charges:
                challan.extra_charges = extra_charges
            if round_amount:
                print("round True")
                challan.round_amount = round_amount
            challan.save()
        print(challan.round_amount, challan.extra_charges)
        cash_amount = decimal.Decimal(request.POST.get('cash_amount') or 0)
        account_amount_1 = decimal.Decimal(request.POST.get('account_amount') or 0)
        actr_no = request.POST.get("actr_no") or None
        ac_less_amount = decimal.Decimal(request.POST.get('ac_less_amount') or 0)
        # total_pay = cash_amount + account_amount_1 + ac_less_amount + payment.payed_amount + round_amount - extra_charges
        total_pay = cash_amount + account_amount_1 + ac_less_amount + payment.payed_amount - extra_charges
        print(total_pay, payment.amount, "@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        # return redirect(challan.get_absolute_url)
        if total_pay > payment.amount:
            messages.warning(request, "Total Amount should be less or equal to {} and it is {}".format(payment.amount, total_pay))
            return redirect(challan.get_payment_add_url)
        if cash_amount:
            cash_transaction = CashTransaction.objects.create(payment=payment, amount=cash_amount, payed_on=timezone.now(), status="DN")
        if account_amount_1:
            bank_account_id_1 = (request.POST.get('bank_account') or None)
            bank_account_1 = get_object_or_404(BankAccount, id=bank_account_id_1, party=party)
            account_transaction_1 = AccountTransaction.objects.create(payment=payment, amount=account_amount_1,
                                                                      bank_account=bank_account_1, actr_no=actr_no)
        if wallet is not None and ac_less_amount:
            wallet_transaction, created = WalletTransaction.objects.get_or_create(payment=payment, wallet=wallet)
            print(created, "--------------------------------------")
            wallet_transaction.amount += ac_less_amount
            wallet_transaction.save()
        payment.save()
        return redirect(challan.get_absolute_url)
    else:
        context = {"challan": challan, "payment": payment}
        if payment.payment_mode == "AL":
            context['wallet'] = wallet
            context['wallet_payable_amount'], context['non_wallet_amount'] = wallet.get_payable_amount(payment.get_remaining_amount)
            print(context)
        return render(request, "payments/add.html", context)


class PaymentListView(LoginRequiredMixin, ListView):

    template_name = "payments/list.html"
    model = Payment
    context_object_name = "payments"
    ordering = "-id"


class PaymentDetailView(LoginRequiredMixin, DetailView):

    template_name = "payments/detail.html"
    model = Payment
    context_object_name = "payment"
    slug_field = "id"
    slug_url_kwarg = "id"
