from django.db.models import signals
from django.dispatch import receiver

from . import tasks as app_tasks
from .models import AppUser


@receiver(signals.post_save, sender=AppUser)
def run_celery_task(sender, instance: AppUser, created, **kwargs):
    print(
        f'Signal from {sender}: '
        f'{instance} was {"created" if created else "updated"}'
    )
    app_tasks.test_celery.delay(instance.username)
