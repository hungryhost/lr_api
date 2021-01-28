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
