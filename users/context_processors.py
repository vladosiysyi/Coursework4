from .views import user_is_manager

def manager_flag(request):
    return {
        'is_manager': user_is_manager(request.user) if request.user.is_authenticated else False
    }
