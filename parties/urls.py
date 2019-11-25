from django.conf.urls import url
from . import views

app_name = "parties"

urlpatterns = [
    url(r"^list/$", views.PartyListView.as_view(), name="list"),
    url(r"^detail/(?P<party_code>[0-9a-zA-Z-]+)/$", views.PartyDetailView.as_view(), name="detail"),
    url(r"^update/(?P<party_code>[0-9a-zA-Z-]+)/$", views.PartyUpdateView.as_view(), name="update"),
    url(r"^add/$", views.PartyAddView.as_view(), name="add"),

    url(r"^wallets/list/$", views.WalletListView.as_view(), name="wallet_list"),
    url(r"^wallet/detail/(?P<id>[0-9]+)/$", views.WalletDetailView.as_view(), name="wallet_detail"),
]
