def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[-1].strip()
	elif request.META.get('HTTP_X_REAL_IP'):
		ip = request.META.get('HTTP_X_REAL_IP')
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip


def error_parser_to_db():
	pass


def created_property_logger(request):
	pass
