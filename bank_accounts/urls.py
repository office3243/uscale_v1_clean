from django.conf.urls import url
from . import views

app_name = "bank_accounts"

urlpatterns = [
    url(r"^list/$", views.BankAccListView.as_view(), name="list"),
    url(r"^add/$", views.BankAccAddView.as_view(), name="add"),
]