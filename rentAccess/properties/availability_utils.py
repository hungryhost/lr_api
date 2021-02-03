from datetime import datetime, timedelta, time, date
import time as tm
import pytz


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


def decompose_big_slot(time_from, time_until):
	num_of_slots = time_until.hour - time_from.hour
	initial_time = time_from.hour

	slots = []
	for i in range(initial_time, initial_time+num_of_slots):
		slot_from = time(i).strftime("%H:%M")
		slot_until = time(i+1).strftime("%H:%M")
		slot_dict = {
			"start": slot_from,
			"end": slot_until
		}
		slots.append(slot_dict)
	return slots


def available_hours_from_db(_property, booking):
	hours_from_db = list(_property.availability.available_hours)
	slots = []
	booked_slots = []
	for i in range(len(hours_from_db)):
		if hours_from_db[i] == "1":
			if i < 23:
				slot_until = time(i + 1).strftime("%H:%M")
				slot_from = time(i).strftime("%H:%M")
			else:
				slot_until = "00:00"
				slot_from = "23:00"
			slot_dict = {
				"start": slot_from,
				"end": slot_until
			}
			slots.append(slot_dict)

	for booking in booking:
		time_from_unaware = booking.booked_from.time()
		time_until_unaware = booking.booked_until.time()

		timezone = _property.property_address.city.city.timezone
		time_from_aware = get_aware_time(unaware_time=time_from_unaware, timezone=timezone)
		time_until_aware = get_aware_time(unaware_time=time_until_unaware, timezone=timezone)
		if time_until_aware.hour - time_from_aware.hour > 1:
			slot_dict_list = decompose_big_slot(time_from_aware, time_until_aware)
			for slot_dict in slot_dict_list:
				booked_slots.append(slot_dict)
		else:
			slot_from = time_from_aware.strftime("%H:%M")
			slot_until = time_until_aware.strftime("%H:%M")
			slot_dict = {
				"start": slot_from,
				"end": slot_until
			}
			booked_slots.append(slot_dict)
	final_slots = [x for x in slots if x not in booked_slots]
	return final_slots


def available_hours_from_time(time_from, time_until):
	hours_between = time_until.hour - time_from.hour
	slots = []
	for i in range(hours_between):

		slot_from = time(time_from.hour + i).strftime("%H:%M")
		slot_until = time(time_from.hour + i + 1).strftime("%H:%M")
		slot_dict = {
			"start": slot_from,
			"end": slot_until
		}
		slots.append(slot_dict)
	return slots, hours_between

