from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm
import time
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from .models import Mailing, MailingAttempt
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from .models import Mailing
from .services import send_mailing_service
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

def user_is_manager(user):
    return user.groups.filter(name='Менеджеры').exists()
logger = logging.getLogger(__name__)
# Статистика с кешем страницы (15 минут)
@method_decorator(cache_page(60 * 15), name='dispatch')
class StatisticsView(TemplateView):
    template_name = 'clients/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if getattr(user, 'is_manager', False):
            attempts = MailingAttempt.objects.all()
            mailings = Mailing.objects.all()
        else:
            mailings = Mailing.objects.filter(owner=user)
            attempts = MailingAttempt.objects.filter(mailing__in=mailings)

        context.update({
            'success_count': attempts.filter(status='success').count(),
            'fail_count': attempts.filter(status='fail').count(),
            'total_sent': attempts.count(),
            'mailings': mailings,
        })
        return context

# Главная панель с кешем страницы
@method_decorator(cache_page(60 * 15), name='dispatch')
class DashboardView(TemplateView):
    template_name = 'clients/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_mailings': Mailing.objects.count(),
            'active_mailings': Mailing.objects.filter(status='started').count(),
            'unique_clients': Client.objects.count()
        })
        return context


# === CLIENTS ===
class ClientListView(ListView):
    model = Client
    template_name = 'clients/client_list.html'

    def get_queryset(self):
        key = f'client_list_{self.request.user.id}'
        queryset = cache.get(key)
        if queryset is None:
            queryset = Client.objects.filter(owner=self.request.user)
            cache.set(key, queryset, 60 * 15)
        return queryset

class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/client_detail.html'

class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        cache.delete(f'client_list_{self.request.user.id}')
        return super().form_valid(form)

class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        cache.delete(f'client_list_{self.request.user.id}')
        return super().form_valid(form)

class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        cache.delete(f'client_list_{request.user.id}')
        return super().delete(request, *args, **kwargs)


# === MESSAGES ===
class MessageListView(ListView):
    model = Message
    template_name = 'clients/message_list.html'

    def get_queryset(self):
        key = f'message_list_{self.request.user.id}'
        queryset = cache.get(key)
        if queryset is None:
            queryset = Message.objects.filter(owner=self.request.user)
            cache.set(key, queryset, 60 * 15)
        return queryset

class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'clients/message_form.html'
    success_url = reverse_lazy('message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        cache.delete(f'message_list_{self.request.user.id}')
        return super().form_valid(form)

class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'clients/message_form.html'
    success_url = reverse_lazy('message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        cache.delete(f'message_list_{self.request.user.id}')
        return super().form_valid(form)

class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'clients/message_confirm_delete.html'
    success_url = reverse_lazy('message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        cache.delete(f'message_list_{request.user.id}')
        return super().delete(request, *args, **kwargs)


# === MAILINGS ===
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'clients/mailing_list.html'

    def get_queryset(self):
        user = self.request.user
        if user_is_manager(user):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'clients/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'clients/mailing_form.html'
    success_url = reverse_lazy('mailing_list')

    def test_func(self):
        user = self.request.user
        if user_is_manager(user):
            # Менеджеры не могут редактировать чужие рассылки
            return self.get_object().owner == user
        return self.get_object().owner == user

    def form_valid(self, form):
        return super().form_valid(form)

class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'clients/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing_list')

    def delete(self, request, *args, **kwargs):
        cache.delete(f'mailing_list_{request.user.id}')
        return super().delete(request, *args, **kwargs)




def send_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    send_mailing_service(mailing)
    return redirect('mailing_list')