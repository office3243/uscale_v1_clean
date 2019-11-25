from . import views
from django.conf.urls import url
from django.contrib.auth.views import LoginView, logout_then_login

app_name = "accounts"

urlpatterns = [
    url(r'^login/$', LoginView.as_view(template_name="accounts/login.html"), name='login'),
    url(r'^logout/$', logout_then_login, name='logout'),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
]
