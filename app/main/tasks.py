import logging
from typing import List

from celery import shared_task
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task
def send_email_celery(
    subject: str, message: str, from_email: str, recipient_list: List[str]
) -> None:
    """
    Celery task which calls the built-in django method django.core.mail.send_mail
    """
    send_mail(
        subject, message, from_email, recipient_list, fail_silently=False,
    )
    logger.info(
        f"""Email sent successfully via a Celery task\n
                subject: {subject}\n
                body: {message}\n
                from_email: {from_email}\n
                to_emails: {str(recipient_list)}"""
    )
