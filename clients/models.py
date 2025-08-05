from django.db import models
from django.utils import timezone
from django.conf import settings


class Client(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f'{self.full_name} <{self.email}>'


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailings'
    )

    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('finished', 'Завершена'),
    ]

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Client)

    def __str__(self):
        return f'Рассылка #{self.pk} — {self.get_status_display()}'

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Client)

    def __str__(self):
        return f'Рассылка #{self.pk} — {self.get_status_display()}'


class MailingAttempt(models.Model):
    ATTEMPT_STATUS = [
        ('success', 'Успешно'),
        ('fail', 'Не успешно'),
    ]

    attempted_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=ATTEMPT_STATUS)
    server_response = models.TextField()
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.mailing} — {self.get_status_display()}'
