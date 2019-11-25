from . import views
from django.conf.urls import url

app_name = "portal"

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),

    url(r'^temp_form_test/$', views.temp_form_test, name="temp_form_test"),

]
