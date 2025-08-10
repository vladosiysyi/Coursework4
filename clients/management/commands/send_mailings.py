from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from clients.models import Mailing, MailingAttempt

class Command(BaseCommand):
    help = 'Отправляет письма по активным рассылкам'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        # Берем только активные рассылки
        mailings = Mailing.objects.filter(
            status='started',
            start_time__lte=now,
            end_time__gte=now
        )

        for mailing in mailings:
            subject = mailing.message.subject
            body = mailing.message.body
            from_email = settings.DEFAULT_FROM_EMAIL
            recipients = mailing.recipients.all()

            for client in recipients:
                try:
                    send_mail(
                        subject=subject,
                        message=body,
                        from_email=from_email,
                        recipient_list=[client.email],
                        fail_silently=False
                    )
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        status='success',
                        server_response=f"Sent to {client.email}"
                    )
                    self.stdout.write(self.style.SUCCESS(f'Отправлено: {client.email}'))
                except Exception as e:
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        status='fail',
                        server_response=str(e)
                    )
                    self.stdout.write(self.style.ERROR(f'Ошибка для {client.email}: {e}'))
