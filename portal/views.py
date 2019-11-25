from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(LoginRequiredMixin, TemplateView):

    template_name = "portal/home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return redirect("cms_admin:dashboard")
        return super().get(request)


def temp_form_test(request):
    if request.POST:
        print(request.POST)
    return render(request, "portal/temp_form_test.html")
