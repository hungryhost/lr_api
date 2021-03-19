from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework import exceptions
from .models import Organisation, OrganisationMember, OrganisationProperty
from userAccount.serializers import UserSerializer
from propertyGroups.serializers import PropertiesListField
from properties.models import Property
from properties.serializers import PropertyListSerializer
User = get_user_model()


class OrganisationListSerializer(serializers.ModelSerializer):
	is_my_organisation = serializers.SerializerMethodField("get_is_my_organisation")

	class Meta:
		model = Organisation
		fields = [
			'id',
			'name',
			'description',
			'website',
			'active',
			'created_at',
			'updated_at',
			'is_confirmed',
			'is_my_organisation',
			'created_at',
			'updated_at'
		]
		read_only_fields = [
			'id',
			'name',
			'description',
			'website',
			'active',
			'created_at',
			'updated_at',
			'is_confirmed',
			'is_my_organisation',
			'created_at',
			'updated_at'
		]

	def get_is_my_organisation(self, obj):
		user = self.context["request"].user
		membership = obj.member_tied_org.all()
		_member = None
		for member in membership:
			if member.user == user:
				_member = member
		if _member is not None and _member.is_creator:
			return True
		return False


class OrganisationCreateSerializer(serializers.ModelSerializer):
	name = serializers.CharField(
		max_length=255,
		allow_blank=False, allow_null=False, required=True)
	website = serializers.CharField(
		max_length=255, allow_blank=False, allow_null=False,
		required=True)
	description = serializers.CharField(
		max_length=500, allow_blank=False, allow_null=False,
		required=True)

	class Meta:
		model = Organisation
		fields = [
			'id',
			'name',
			'description',
			'website',
			'active',
			'created_at',
			'updated_at',
			'is_confirmed'
		]
		read_only_fields = [
			'id',
			'active',
			'created_at',
			'updated_at',
			'is_confirmed'
		]

	def create(self, validated_data):
		website = validated_data.get('website')
		name = validated_data.get('name')
		description = validated_data.get('description')
		try:
			membership = OrganisationMember.objects.get(
				user=self.context['request'].user,
				is_creator=True
			)
		except OrganisationMember.DoesNotExist:
			membership = None
		if membership:
			if membership.organisation.active:
				raise serializers.ValidationError({
					"user": "User is already a creator of an active organisation."
				})
		user = User.objects.get(pk=self.context['request'].user.id)
		user.plan = 'CORP'

		organisation = Organisation(
			name=name,
			website=website,
			description=description,
			active=True,
			is_confirmed=False
		)

		member = OrganisationMember(
			organisation=organisation,
			user=self.context['request'].user,
			is_creator=True,
			can_add_properties=True,
			can_delete_properties=True,
			can_book_properties=True,
			recursive_ownership=True,
			can_add_members=True,
			can_remove_members=True,
			can_manage_members=True
		)
		user.save()
		organisation.save()
		member.save()
		return organisation


class OrganisationRetrieveUpdateSerializer(serializers.ModelSerializer):

	class Meta:
		model = Organisation
		fields = [
			'id',
			'name',
			'description',
			'website',
			'active',
			'created_at',
			'updated_at',
			'is_confirmed'
		]
		read_only_fields = [
			'id',
			'created_at',
			'updated_at',
			'is_confirmed'
		]


class OrganisationMemberSerializer(serializers.ModelSerializer):
	user = UserSerializer(many=False, read_only=True)
	member_id = serializers.IntegerField(source='id')

	class Meta:
		model = OrganisationMember
		fields = [
			'member_id',
			'user',
			'is_creator',
			'can_add_properties',
			'can_delete_properties',
			'can_book_properties',
			'recursive_ownership',
			'can_add_members',
			'can_remove_members',
			'can_manage_members',
			'joined_with_code',
			'joined_with_link',
			'added_by_user_id',
			'created_at',
			'updated_at'
		]
		read_only_fields = [
			'member_id',
			'user',
			'is_creator',
			'joined_with_code',
			'joined_with_link',
			'added_by_user_id',
			'created_at',
			'updated_at'
		]


class UserOrganisationMemberCreateSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(required=True, source='user.email')
	can_add_properties = serializers.BooleanField(required=True)
	can_delete_properties = serializers.BooleanField(required=True)
	can_book_properties = serializers.BooleanField(required=True)
	recursive_ownership = serializers.BooleanField(required=False)
	can_add_members = serializers.BooleanField(required=True)
	can_remove_members = serializers.BooleanField(required=True)
	can_manage_members = serializers.BooleanField(required=True)

	class Meta:
		model = OrganisationMember
		fields = [
			"email",
			"can_add_properties",
			"can_delete_properties",
			"can_book_properties",
			"recursive_ownership",
			"can_add_members",
			"can_remove_members",
			"can_manage_members",
			"created_at",
			"updated_at"
		]
		read_only_fields = [
			'created_at',
			'updated_at'
		]

	def create(self, validated_data):
		user_data = validated_data.get("user")
		email = user_data.get("email")
		try:
			user = User.objects.get(email=email)
		except User.DoesNotExist:
			raise serializers.ValidationError({
				"user": "user with given email does not exist."
			}
			)
		if OrganisationMember.objects.all().filter(
			user=user,
			organisation_id=self.context["organisation_id"]
		).exists():
			raise serializers.ValidationError({
				"user": "user with given email is already a member."
			}
			)
		can_add_properties = validated_data.get("can_add_properties")
		can_delete_properties = validated_data.get("can_delete_properties")
		can_book_properties = validated_data.get("can_book_properties")
		recursive_ownership = validated_data.get("recursive_ownership")
		can_add_members = validated_data.get("can_add_members", None)
		can_remove_members = validated_data.get("can_remove_members")
		can_manage_members = validated_data.get("can_manage_members")

		organisation_id = self.context["organisation_id"]
		if recursive_ownership is None:
			recursive_ownership = False

		member = OrganisationMember(
			user=user,
			organisation_id=organisation_id,
			is_creator=False,
			can_add_properties=can_add_properties,
			can_delete_properties=can_delete_properties,
			can_book_properties=can_book_properties,
			recursive_ownership=recursive_ownership,
			can_add_members=can_add_members,
			can_remove_members=can_remove_members,
			can_manage_members=can_manage_members,
			added_by_user_id=self.context['request'].user.id
		)
		member.save()
		return member


class PropertyOrganisationMemberCreateSerializer(serializers.ModelSerializer):
	r"""
	A serializer class we use for adding properties to groups;
	"""
	properties = PropertiesListField(allow_null=False, allow_empty=False, required=True)

	class Meta:
		model = OrganisationProperty
		fields = [
			"id",
			"organisation",
			"properties",
			"created_at",
			"updated_at"
		]
		read_only_fields = [
			"id",
			"organisation",
			"created_at",
			"updated_at"
		]

	def create(self, validated_data):
		properties_input = validated_data.get('properties', None)

		properties_existing = Property.objects.all().prefetch_related(
			"owners",
			"owners__user"
		).filter(id__in=properties_input)
		if not properties_existing:
			# here we check whether the properties with given ids exist
			raise serializers.ValidationError({"Properties with given ids do not exist."})
		if OrganisationProperty.objects.all().filter(
				premises_id__in=properties_input,
				organisation_id=self.context['organisation_id']).exists():
			# here we check if properties are already in the group
			raise serializers.ValidationError("Properties already in the group.")
		# TODO: maybe find a way to move that to views since the permissions should be checked there

		for premises in properties_existing:
			ownerships = premises.owners.all()
			# this is step is required to to skip needless queries
			current_user = None
			# we check whether the current user has permissions to add
			# the property to groups
			for owner in ownerships:
				if owner.user.id == self.context["request"].user.id:
					current_user = owner
			if not (current_user and current_user.can_add_to_organisation):
				raise exceptions.PermissionDenied
		# finally we check if the user has permissions to add properties
		# to the group
		if not OrganisationMember.objects.all().filter(
				user=self.context["request"].user,
				organisation_id=self.context['organisation_id'],
				can_add_properties=True
		).exists():
			raise exceptions.PermissionDenied

		if properties_input:
			properties_instance = [
				OrganisationProperty(
					organisation_id=self.context['organisation_id'], premises_id=premises,
					added_by=self.context['request'].user
				)
				for premises in properties_input]
			properties = OrganisationProperty.objects.bulk_create(properties_instance)
			return properties


class OrganisationPropertyList(serializers.ModelSerializer):
	added_property = PropertyListSerializer(many=False, source='premises')

	class Meta:
		model = OrganisationProperty
		fields = [
			"id",
			"added_property",
			"created_at",
			"updated_at"
		]
		read_only_fields = [
			"id",
			"added_property"
			"created_at",
			"updated_at"
		]