import time
import logging
from django.core.mail import send_mail
from django.conf import settings
from .models import Mailing, MailingAttempt
from django.core.cache import cache

logger = logging.getLogger(__name__)

def send_mailing_service(mailing: Mailing):
    recipients = mailing.recipients.all()
    subject = mailing.message.subject
    body = mailing.message.body
    from_email = settings.DEFAULT_FROM_EMAIL

    for client in recipients:
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[client.email],
                fail_silently=False,
            )

            MailingAttempt.objects.create(
                mailing=mailing,
                status='success',
                server_response=f"Sent to {client.email}",
            )

            logger.info(f"Письмо отправлено на {client.email}")
            time.sleep(2)  # Задержка, чтобы избежать блокировки SMTP

        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                status='fail',
                server_response=f"Failed for {client.email}: {str(e)}",
            )
            logger.error(f"Ошибка отправки на {client.email}: {str(e)}")

    mailing.status = 'started'
    mailing.save()

    cache.delete(f'mailing_list_{mailing.owner.id}')
