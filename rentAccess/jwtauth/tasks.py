from celery import shared_task
from celery.decorators import task
from celery.utils.log import get_task_logger
from time import sleep
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.management import call_command
from django.template import Context
from django.template.loader import get_template
from django.conf import settings

logger = get_task_logger(__name__)


@task(name='send_email_confirmation')
def email_confirmation_task(duration, data):
    """
    This method sends confirmation email to the new user.

    :param duration: duration of the delay
    :param data: dictionary of data

    """
    #print('started_task')
    sleep(duration)
    email_body = "Добро пожаловать на lockandrent.ru! Ваша учётная запись создана, вы можете создавать помещения и бронирования.\n" \
           "Перед этим подтвердите учётную запись по ссылке:"
    plaintext = get_template('generic_email_template_with_button.txt')
    htmly = get_template('generic_email_template_with_button.html')
    context = {'full_name': data["full_name"], 'link': data["link"], 'email_body': email_body}
    text_content = plaintext.render(context)
    html_content = htmly.render(context)
    message = EmailMultiAlternatives("Подтвердите вашу учётную запись", text_content, 'LockAndRent <no-reply@lockandrent.ru>',
                                     [data["email"]])
    # send_mail(data["subject"], data["body"], EMAIL_HOST_USER, [data["email"]])
    message.attach_alternative(html_content, "text/html")
    message.send()
    #print('ended_task')


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
