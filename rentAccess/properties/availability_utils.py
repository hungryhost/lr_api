from datetime import datetime, timedelta, time, date
import time as tm
import pytz
from bookings.models import Booking


def get_aware_time(unaware_time, timezone):
	timezone = pytz.timezone(timezone)
	aware = pytz.utc.localize(datetime.combine(datetime.today(), unaware_time)).astimezone(timezone).time()
	return aware


def available_days_to_db(available_days):
	days = list('0000000')
	possible_days = [0, 1, 2, 3, 4, 5, 6]
	for available_day in available_days:
		if available_day in possible_days:
			days[available_day] = '1'
	return "".join(days)


def available_days_from_db(available_days):
	days_from_db = list(available_days)
	days = []
	for i in range(0, 7):
		if days_from_db[i] == '1':
			days.append(i)
	return days


def available_hours_to_db(time_from, time_until):
	hours = '000000000000000000000000'
	list_hours = list(hours)
	initial_hour = time_from.hour
	diff = time_until.hour - initial_hour
	for i in range(initial_hour, initial_hour+diff):
		list_hours[i] = '1'
	return "".join(list_hours)


def decompose_nightly_big_slot(time_from, time_until, b_date=None, end_b_date=None):

	start_hour = time_from.hour
	end_hour = time_until.hour
	iterations_current_day = 24 - start_hour
	iterations_next_day = end_hour
	nightly_slots = []
	for i in range(iterations_current_day):
		if i + start_hour > 22:
			slot_until = datetime.combine(b_date + timedelta(days=1), time(0)).strftime("%Y-%m-%dT%H:%M")
			slot_from = datetime.combine(b_date, time(23)).strftime("%Y-%m-%dT%H:%M")
		else:
			slot_until = datetime.combine(b_date, time(start_hour + i + 1)).strftime("%Y-%m-%dT%H:%M")
			slot_from = datetime.combine(b_date, time(start_hour + i)).strftime("%Y-%m-%dT%H:%M")
		slot_dict = {
			"start": slot_from,
			"end"  : slot_until
		}
		nightly_slots.append(slot_dict)
	if iterations_next_day != 0:
		start_hour = 0
	for i in range(iterations_next_day):
		slot_until = datetime.combine(b_date + timedelta(days=1), time(start_hour + i + 1)).strftime(
			"%Y-%m-%dT%H:%M")
		slot_from = datetime.combine(b_date + timedelta(days=1), time(start_hour + i)).strftime("%Y-%m-%dT%H:%M")
		slot_dict = {
			"start": slot_from,
			"end"  : slot_until
		}
		nightly_slots.append(slot_dict)
	return nightly_slots


def decompose_daily_slots(time_from, time_until, b_date=None):
	num_of_slots = time_until.hour - time_from.hour
	initial_time = time_from.hour
	slots = []
	for i in range(initial_time, initial_time + num_of_slots):
		slot_until = datetime.combine(b_date, time(i + 1)).strftime("%Y-%m-%dT%H:%M")
		slot_from = datetime.combine(b_date, time(i)).strftime("%Y-%m-%dT%H:%M")
		slot_dict = {
			"start": slot_from,
			"end"  : slot_until
		}
		slots.append(slot_dict)
	return slots


def get_slots_from_bookings(bookings, timezone, b_date):
	booked_slots = []
	for booking in bookings:
		time_from_unaware = booking.booked_from.time()
		time_until_unaware = booking.booked_until.time()

		time_from_aware = get_aware_time(unaware_time=time_from_unaware, timezone=timezone)
		time_until_aware = get_aware_time(unaware_time=time_until_unaware, timezone=timezone)
		timezone_mark = pytz.timezone(timezone)
		aware_from = pytz.utc.localize(
			datetime(
				booking.booked_from.year,
				booking.booked_from.month,
				booking.booked_from.day,
				booking.booked_from.hour,
				booking.booked_from.minute,
			)).astimezone(timezone_mark)
		aware_until = pytz.utc.localize(
			datetime(
				booking.booked_until.year,
				booking.booked_until.month,
				booking.booked_until.day,
				booking.booked_until.hour,
				booking.booked_until.minute,
			)).astimezone(timezone_mark)

		if time_until_aware.hour - time_from_aware.hour > 1 or aware_until.weekday() != aware_from.weekday():
			if aware_until.weekday() != aware_from.weekday():
				for i in range(aware_until.day - aware_from.day + 1):
					slot_dict_list = decompose_nightly_big_slot(time_from_aware, time_until_aware,
					                                            b_date=b_date)

			else:
				slot_dict_list = decompose_daily_slots(time_from_aware, time_until_aware, b_date=date(
					booking.booked_until.year,
					booking.booked_until.month,
					booking.booked_until.day
				))
			for slot_dict in slot_dict_list:
				booked_slots.append(slot_dict)

		else:
			slot_until = datetime.combine(b_date, time_until_aware).strftime("%Y-%m-%dT%H:%M")
			slot_from = datetime.combine(b_date, time_from_aware).strftime("%Y-%m-%dT%H:%M")
			slot_dict = {
				"start": slot_from,
				"end": slot_until
			}
			booked_slots.append(slot_dict)
	return booked_slots


def decompose_nightly_slots(av_from, av_until, b_date, open_days):
	start_hour = av_from.hour
	end_hour = av_until.hour
	iterations_current_day = 24 - start_hour
	iterations_next_day = end_hour
	nightly_slots = []
	for i in range(iterations_current_day):
		if i + start_hour > 22:
			slot_until = datetime.combine(b_date+timedelta(days=1), time(0)).strftime("%Y-%m-%dT%H:%M")
			slot_from = datetime.combine(b_date, time(23)).strftime("%Y-%m-%dT%H:%M")
		else:
			slot_until = datetime.combine(b_date, time(start_hour+i+1)).strftime("%Y-%m-%dT%H:%M")
			slot_from = datetime.combine(b_date, time(start_hour+i)).strftime("%Y-%m-%dT%H:%M")
		slot_dict = {
			"start": slot_from,
			"end"  : slot_until
		}
		nightly_slots.append(slot_dict)
	if iterations_next_day != 0:
		start_hour = 0
	days = available_days_from_db(open_days)
	if b_date.weekday() + 1 in days:
		for i in range(iterations_next_day):
			slot_until = datetime.combine(b_date+timedelta(days=1), time(start_hour+i+1)).strftime("%Y-%m-%dT%H:%M")
			slot_from = datetime.combine(b_date+timedelta(days=1), time(start_hour+i)).strftime("%Y-%m-%dT%H:%M")
			slot_dict = {
				"start": slot_from,
				"end"  : slot_until
			}
			nightly_slots.append(slot_dict)
	return nightly_slots


def available_hours_from_db(_property, b_date=None):
	hours_from_db = list(_property.availability.available_hours)
	slots = []
	timezone = _property.property_address.city.city.timezone
	if _property.availability.available_from >= _property.availability.available_until:
		bookings = Booking.objects.all().filter(
			booked_property=_property,
			booked_from__date__gte=b_date,
			booked_until__date__lte=b_date+timedelta(1)
		)
		nightly_slots = decompose_nightly_slots(
			_property.availability.available_from,
			_property.availability.available_until,
			b_date,
			_property.availability.open_days
		)
		booked_slots = get_slots_from_bookings(bookings=bookings, timezone=timezone, b_date=b_date)

		final_slots = [x for x in nightly_slots if x not in booked_slots]
		#print(booked_slots)
		#print(nightly_slots)
		#print(final_slots)
		return final_slots
	bookings = Booking.objects.all().filter(
		booked_property=_property,
		booked_from__date=b_date,
		booked_until__date=b_date
	)
	for i in range(len(hours_from_db)):
		if hours_from_db[i] == "1":
			if i < 23:
				slot_until = datetime.combine(b_date, time(i+1)).strftime("%Y-%m-%dT%H:%M")
				slot_from = datetime.combine(b_date, time(i)).strftime("%Y-%m-%dT%H:%M")
			else:
				slot_until = datetime.combine(b_date+timedelta(days=1), time(0)).strftime("%Y-%m-%dT%H:%M")
				slot_from = datetime.combine(b_date, time(23)).strftime("%Y-%m-%dT%H:%M")
			slot_dict = {
				"start": slot_from,
				"end": slot_until
			}
			slots.append(slot_dict)
	booked_slots = get_slots_from_bookings(bookings=bookings, timezone=timezone, b_date=b_date)

	final_slots = [x for x in slots if x not in booked_slots]
	return final_slots


def decompose_incoming_booking(datetime_from, datetime_until, timezone):
	# TODO: handle nightly bookings
	time_from_unaware = datetime_from.time()
	time_until_unaware = datetime_until.time()
	booked_slots = []
	time_from_aware = get_aware_time(unaware_time=time_from_unaware, timezone=timezone)
	time_until_aware = get_aware_time(unaware_time=time_until_unaware, timezone=timezone)
	if time_until_aware.hour - time_from_aware.hour > 1:
		slot_dict_list = decompose_nightly_big_slot(time_from_unaware, time_until_unaware, b_date=datetime_from.date())
		for slot_dict in slot_dict_list:
			booked_slots.append(slot_dict)
	else:
		slot_from = datetime_from.strftime("%Y-%m-%dT%H:%M")
		slot_until = datetime_until.strftime("%Y-%m-%dT%H:%M")
		slot_dict = {
			"start": slot_from,
			"end": slot_until
		}
		booked_slots.append(slot_dict)
	return booked_slots
