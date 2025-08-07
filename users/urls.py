from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import register_view, profile_view, profile_edit_view,UserListView
from .views import UserListView, UserBlockToggleView

urlpatterns = [
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
    path('list/', UserListView.as_view(), name='user_list'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('block/<int:pk>/', UserBlockToggleView.as_view(), name='user_block_toggle'),


]
