from django.conf.urls import url
from . import views

app_name = "rates"

urlpatterns = [
    url(r"^$", views.RatesView.as_view(), name="rates_view"),
    url(r"^add/$", views.RateGroupAddView.as_view(), name="rate_group_add"),
    url(r"^rate_groups/list/$", views.RateGroupListView.as_view(), name="rate_group_list"),
    url(r"^rate_group/(?P<id>[0-9]+)/detail$", views.RateGroupDetailView.as_view(), name="rate_group_detail"),
    url(r"^rate_group/(?P<id>[0-9]+)/update$", views.RateGroupUpdateView.as_view(), name="rate_group_update"),

    url(r"^material_rate/(?P<id>[0-9]+)/update$", views.MaterialRateUpdateView.as_view(), name="material_rate_update"),
    # url(r"^rate_group/detail/(?P<party_code>[0-9a-zA-Z-]+)/$", views.RateGroupDetailView.as_view(), name="rate_group_detail"),
    # url(r"^rate_group/add/$", views.RateGroupAdd.as_view(), name="rate_group_add"),
]
