from celery import shared_task
from celery.decorators import task
from celery.utils.log import get_task_logger
from time import sleep
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.management import call_command
from django.template import Context
from django.template.loader import get_template
from rentAccess.settings import EMAIL_HOST_USER
logger = get_task_logger(__name__)


@task(name='send_email_confirmation')
def email_confirmation_task(duration, data):
    """
    This method sends confirmation email to the new user.

    :param duration: duration of the delay
    :param data: dictionary of data

    """
    sleep(duration)
    plaintext = get_template('email_confirmation.txt')
    htmly = get_template('email_confirmation.html')
    context = {'username': data["first_name"], 'confirmation_link': data["confirmation_link"]}
    text_content = plaintext.render(context)
    html_content = htmly.render(context)
    message = EmailMultiAlternatives(data["subject"], text_content, EMAIL_HOST_USER, [data["email"]])
    # send_mail(data["subject"], data["body"], EMAIL_HOST_USER, [data["email"]])
    message.attach_alternative(html_content, "text/html")
    message.send()


@task(name="delete_blacklisted_tokens")
def delete_blacklisted_tokens():
    """
    This method removes all blacklisted tokens.
    Version: 1.0
    """
    # local import of model, otherwise it won't work
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
    BlacklistedToken.objects.all().delete()
    # print('Deleted')
