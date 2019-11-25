from django.conf.urls import url
from . import views

app_name = "cms_admin"

urlpatterns = [
    url(r"^dashboard/$", views.DashboardView.as_view(), name="dashboard"),
    url(r'^payments/list/$', views.PaymentListView.as_view(), name="payments_list"),
    url(r'^payments/detail/(?P<id>[0-9]+)$', views.PaymentDetailView.as_view(), name="payments_detail"),
    url(r'^payments/account_transactions/list/$', views.AccountTransactionListView.as_view(), name="account_transactions_list"),
    url(r'^payments/account_transactions/detail/(?P<id>[0-9]+)$', views.AccountTransactionDetailView.as_view(),
        name="account_transactions_detail"),
    url(r'^payments/account_transactions/update/(?P<id>[0-9]+)$', views.AccountTransactionUpdateView.as_view(),
        name="account_transactions_update"),

    url(r'^wallets/list/$', views.WalletListView.as_view(), name="wallet_list"),
    url(r'^wallets/update/(?P<id>[0-9]+)/$', views.WalletUpdateView.as_view(), name="wallet_update"),
    url(r'^wallets/wallet_advances/list/$', views.WalletAdvanceListView.as_view(), name="wallet_advances_list"),
    url(r'^wallets/wallet_advances/create/$', views.WalletAdvanceCreateView.as_view(), name="wallet_advances_create"),
]
