from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserCreationForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})


@method_decorator(cache_page(60 * 15), name='dispatch')
class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = cache.get('cached_user_list')
        if not queryset:
            queryset = super().get_queryset()
            cache.set('cached_user_list', queryset, 60 * 15)  # кеш на 15 минут
        return queryset


class UserBlockToggleView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    fields = []  # никаких полей в форме
    template_name = 'users/user_block_form.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        user = form.instance
        user.is_active = not user.is_active  # переключаем активность
        user.save()
        cache.delete('cached_user_list')  # сбрасываем кеш после изменения
        return super().form_valid(form)
