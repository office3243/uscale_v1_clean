from django.conf.urls import url
from . import views

app_name = "materials"

urlpatterns = [
    url(r"^list/$", views.MaterialListView.as_view(), name="list"),
    url(r"^detail/(?P<material_code>[0-9a-zA-Z-\w]+)/$", views.MaterialDetailView.as_view(), name="detail"),
]
