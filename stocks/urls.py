from django.conf.urls import url
from . import views


app_name = "stocks"


urlpatterns = [
    url(r'^view/$', views.StockView.as_view(), name="view"),
    url(r'^(?P<day>[0-9]+)/(?P<month>[0-9]+)/(?P<year>[0-9]{4})/$', views.DateStockDetailView.as_view(), name="date_stock_detail"),
    url(r'^date_list/$', views.DateStockListView.as_view(), name="date_list"),
]
