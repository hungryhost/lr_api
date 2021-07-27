import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = User
	first_name = factory.Faker(
		'first_name'
	)
	last_name = factory.Faker(
		'last_name'
	)
	email = factory.Sequence(lambda n: "user_%d@lockandrent.ru" % n)
	password = factory.PostGenerationMethodCall('set_password', 'adm1n')
