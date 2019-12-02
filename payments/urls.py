from django.conf.urls import url
from . import views

app_name = "payments"

urlpatterns = [

    url(r"^add/(?P<challan_no>[0-9a-zA-Z-]+)/$", views.add, name="add"),
    url(r"^list/$", views.PaymentListView.as_view(), name="list"),
    url(r"^detail/(?P<id>[0-9]+)/$", views.PaymentDetailView.as_view(), name="detail"),
    # url(r"^wallet_transaction/detail/(?P<id>[z0-9]+)/$", views.WalletTransactionDetail.as_view(), name="wtr_detail"),
    # url(r"^account_transaction/detail/(?P<id>[0-9]+)/$", views.PaymentDetailView.as_view(), name="actr_detail"),
    # url(r"^cash_transaction/detail/(?P<id>[0-9]+)/$", views.PaymentDetailView.as_view(), name="cash_tr_detail"),
]
