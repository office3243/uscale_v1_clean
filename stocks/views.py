from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.views.generic import DeleteView, CreateView, UpdateView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import MaterialStock, create_todays_stocks
from django.utils import timezone
import datetime
from django.http import Http404


class DateStockDetailView(LoginRequiredMixin, TemplateView):

    template_name = "stocks/date_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        stock_date = timezone.datetime(day=int(self.kwargs['day']), month=int(self.kwargs['month']), year=int(self.kwargs['year'])).date()
        stocks = MaterialStock.objects.filter(date=stock_date)
        if not stocks.exists():
            return Http404("Stock Date Not Found")
        for stock in stocks:
            stock.save()
        context['stocks'] = stocks
        context['date'] = stock_date
        context['previous_date'] = stock_date - timezone.timedelta(days=1)
        context['next_date'] = stock_date + timezone.timedelta(days=1)
        return context


class StockView(LoginRequiredMixin, TemplateView):

    template_name = "stocks/view.html"


class DateStockListView(LoginRequiredMixin, TemplateView):

    template_name = "stocks/date_list.html"

    def get_context_data(self, **kwargs):
        create_todays_stocks()
        context = super().get_context_data()
        context['dates'] = sorted(set(MaterialStock.objects.order_by("date").values_list("date", flat=True)), key=lambda x: x, reverse=True)
        return context
