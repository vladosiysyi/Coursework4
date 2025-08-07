from django.core.management.base import BaseCommand
from django.utils import timezone
from clients.models import Mailing, Client, MailingAttempt
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Send scheduled mailings'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        mailings = Mailing.objects.filter(status='started', start_time__lte=now, end_time__gte=now)

        for mailing in mailings:
            clients = mailing.clients.all()
            for client in clients:
                try:
                    send_mail(
                        subject=mailing.message.subject,
                        message=mailing.message.body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[client.email],
                        fail_silently=False,
                    )
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        client=client,
                        status='success',
                        server_response='Email sent successfully'
                    )
                    self.stdout.write(self.style.SUCCESS(f'Sent to {client.email}'))
                except Exception as e:
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        client=client,
                        status='failed',
                        server_response=str(e)
                    )
                    self.stdout.write(self.style.ERROR(f'Failed to send to {client.email}: {str(e)}'))
