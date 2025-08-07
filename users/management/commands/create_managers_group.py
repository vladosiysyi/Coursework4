from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Создаёт группу Менеджеры с правами отключать рассылки и блокировать пользователей'

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name='Менеджеры')

        permissions = Permission.objects.filter(codename__in=[
            'can_disable_mailing',
            'can_block_user',
        ])
        group.permissions.set(permissions)
        group.save()

        self.stdout.write(self.style.SUCCESS('Группа Менеджеры создана'))
