import pytz


def utc_to_aware(unaware_time, timezone):
	timezone = pytz.timezone(timezone)
	return timezone.localize(unaware_time)

