import random
import string


def generate_random_string(length=10):
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(length))


def generate_random_list_of_strings(size=5, length=10):
	list_of_strings = []
	for i in range(size):
		list_of_strings.append(generate_random_string(length))
	return list_of_strings


def generate_random_list_of_numbers(size=5, a=100, b=99999):
	list_of_numbers = []
	for i in range(size):
		list_of_numbers.append(random.randint(a, b))
	return list_of_numbers
