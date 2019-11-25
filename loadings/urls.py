from django.conf.urls import url
from . import views

app_name = "loadings"

urlpatterns = [
    url(r'^add/$', views.LoadingAddView.as_view(), name="add"),
    url(r'^entries/(?P<id>[0-9]+)/$', views.entries, name="entries"),
    url(r"^list/$", views.LoadingListView.as_view(), name="list"),
    url(r'^detail/(?P<id>[0-9]+)/$', views.LoadingDetailView.as_view(), name="detail"),

]