from celery import shared_task
from celery.decorators import task
from celery.utils.log import get_task_logger
from time import sleep
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.management import call_command
from django.template import Context
from django.template.loader import get_template
from django.conf import settings
from django.contrib.auth import get_user_model

logger = get_task_logger(__name__)


@task(name='send_booking_email_to_client')
def send_booking_email_to_client(duration, data):
	"""
	This method sends confirmation email to the new user.

	:param has_key:
	:param duration: duration of the delay
	:param data: dictionary of data

	"""
	from properties.models import Property, PremisesAddress, LockWithProperty
	from register.models import Key
	User = get_user_model()
	booked_property = Property.objects.get(id=data['p_id'])
	address = PremisesAddress.objects.get(premises_id=data['p_id'])

	if User.objects.filter(email=data['email']).exists():
		user = User.objects.get(email=data['email'])
		full_name = user.first_name + ' ' + user.last_name
	else:
		full_name = None

	if data['has_key']:
		key = Key.objects.get(pk=data["keys"][0]['key'])
		email_body = f"Бронирование успешно создано! \n" \
			f"Номер бронирования: {data['b_id']}. \n" \
			f"Доступ к помещению с {data['b_start']} по {data['b_end']}.\n" \
			f"Код доступа: {key.code}.\n"
	else:
		email_body = f"Бронирование успешно создано! \n" \
			f"Номер бронирования: {data['b_id']}. \n" \
			f"Доступ к помещению с {data['b_start']} по {data['b_end']}. \n" \

	header = f'Здравствуйте, {full_name}!'
	header_empty = f'Здравствуйте!'
# print('started_task')
	sleep(duration)
	plaintext = get_template('generic_email_template.txt')
	htmly = get_template('generic_email_template.html')
	if full_name:
		context = {'header': header, 'email_body': email_body}
	else:
		context = {'header': header_empty, 'email_body': email_body}
	text_content = plaintext.render(context)
	html_content = htmly.render(context)
	message = EmailMultiAlternatives('Бронирование создано!', text_content, 'LockAndRent <bookings@lockandrent.ru>',
	                                 [data["email"]])
	# send_mail(data["subject"], data["body"], EMAIL_HOST_USER, [data["email"]])
	message.attach_alternative(html_content, "text/html")
	message.send()


