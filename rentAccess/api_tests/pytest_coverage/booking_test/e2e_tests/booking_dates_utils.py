import datetime
import pytz


def get_booking_date(date):
	return date.strftime("%Y-%m-%d")


def get_booking_datetime(datetime_, timezone):
	tz = pytz.timezone(timezone)
	datetime_ = tz.localize(datetime_)
	return datetime_.strftime("%Y-%m-%dT%H:%M")
