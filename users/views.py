from django.contrib.auth import login, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import CustomUserCreationForm
from .models import CustomUser


User = get_user_model()


def user_is_manager(user):
    """Проверка — состоит ли пользователь в группе 'Менеджеры'."""
    return user.groups.filter(name='Менеджеры').exists()


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



class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Список пользователей — доступен только менеджерам с правом блокировки."""
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        user = self.request.user
        return user_is_manager(user) and user.has_perm('users.can_block_user')

    def get_queryset(self):
        # исключаем админов и менеджеров
        return CustomUser.objects.exclude(
            groups__name__in=['Менеджеры', 'Администраторы']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаём готовый флаг в шаблон, чтобы там не вызывать filter(...)
        context['is_manager_with_perm'] = self.test_func()
        return context


class UserBlockToggleView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Включение/выключение активности пользователя."""
    def test_func(self):
        return user_is_manager(self.request.user) and self.request.user.has_perm('users.can_block_user')

    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        return render(request, 'users/user_block_form.html', {'object': user})

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_active = not user.is_active
        user.save()
        return redirect('user_list')
