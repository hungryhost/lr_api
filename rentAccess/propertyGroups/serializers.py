from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework import exceptions
from .models import PropertyGroup, PropertyGroupMembership, UserGroupMembership
from userAccount.serializers import UserSerializer
from properties.serializers import PropertyListSerializer
from properties.models import Property

User = get_user_model()


class UserGroupMemberListSerializer(serializers.ModelSerializer):
	user = UserSerializer(many=False, read_only=True)
	can_add_properties = serializers.BooleanField(required=True)
	can_delete_properties = serializers.BooleanField(required=True)
	can_book_properties = serializers.BooleanField(required=True)
	recursive_ownership = serializers.BooleanField(required=False)
	can_add_members = serializers.BooleanField(required=True)
	can_remove_members = serializers.BooleanField(required=True)
	can_manage_members = serializers.BooleanField(required=True)

	class Meta:
		model = UserGroupMembership
		fields = [
			"user",
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
			"user",
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


class UserGroupMemberCreateSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(required=True, source='user.email')
	can_add_properties = serializers.BooleanField(required=True)
	can_delete_properties = serializers.BooleanField(required=True)
	can_book_properties = serializers.BooleanField(required=True)
	recursive_ownership = serializers.BooleanField(required=False)
	can_add_members = serializers.BooleanField(required=True)
	can_remove_members = serializers.BooleanField(required=True)
	can_manage_members = serializers.BooleanField(required=True)

	class Meta:
		model = UserGroupMembership
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
			raise serializers.ValidationError(
				"user: user with given email does not exist."
			)
		can_add_properties = validated_data.get("can_add_properties")
		can_delete_properties = validated_data.get("can_delete_properties")
		can_book_properties = validated_data.get("can_book_properties")
		recursive_ownership = validated_data.get("recursive_ownership")
		can_add_members = validated_data.get("can_add_members", None)
		can_remove_members = validated_data.get("can_remove_members")
		can_manage_members = validated_data.get("can_manage_members")

		group_id = self.context["group_id"]
		if recursive_ownership is None:
			recursive_ownership = False
		if UserGroupMembership.objects.all().filter(
			user=user,
			group_id=group_id
		).exists():
			raise serializers.ValidationError({
				"user": "user with given email is already a member."
			}
			)
		member = UserGroupMembership(
			user=user,
			group_id=group_id,
			is_creator=False,
			can_add_properties=can_add_properties,
			can_delete_properties=can_delete_properties,
			can_book_properties=can_book_properties,
			recursive_ownership=recursive_ownership,
			can_add_members=can_add_members,
			can_remove_members=can_remove_members,
			can_manage_members=can_manage_members,
		)
		member.save()
		return member


class GroupCreateSerializer(serializers.ModelSerializer):
	title = serializers.CharField(max_length=255, required=True, allow_blank=False)
	description = serializers.CharField(max_length=500, required=True, allow_blank=False)
	id = serializers.IntegerField(read_only=True)

	class Meta:
		model = PropertyGroup
		fields = [
			"id",
			"title",
			"description",
			"created_at",
			"updated_at"
		]
		read_only_fields = [
			'id',
			'created_at',
			'updated_at'
		]

	def create(self, validated_data):
		title = validated_data.get("title")
		description = validated_data.get("description")

		group = PropertyGroup(
			title=title,
			description=description
		)
		group.save()
		member = UserGroupMembership(
			user=self.context["request"].user,
			group=group,
			is_creator=True,

			can_add_properties=True,
			can_delete_properties=True,

			can_book_properties=True,

			recursive_ownership=True,

			can_add_members=True,
			can_remove_members=True,
			can_manage_members=True,
		)
		member.save()
		return group


class GroupListSerializer(serializers.ModelSerializer):
	is_my_group = serializers.SerializerMethodField("get_is_my_group")

	class Meta:
		model = PropertyGroup
		fields = [
			"id",
			"title",
			"is_my_group",
			"description",
			"created_at",
			"updated_at"
		]
		read_only_fields = [
			"id",
			"title",
			"is_my_group",
			"description",
			"created_at",
			"updated_at"
		]

	def get_is_my_group(self, obj):
		user = self.context["request"].user
		membership = obj.property_groups.all()
		_member = None
		for member in membership:
			if member.user == user:
				_member = member
		if _member is not None and _member.is_creator:
			return True
		return False


class PropertyGroupMemberListSerializer(serializers.ModelSerializer):
	property = PropertyListSerializer(read_only=True, source='premises')
	group = GroupListSerializer(read_only=True)

	class Meta:
		model = PropertyGroupMembership
		fields = [
			"id",
			"group",
			"property",
			"created_at",
			"updated_at"
		]
		read_only_fields = [
			"id",
			"group",
			"property",
			"created_at",
			"updated_at"
		]


class PropertiesListField(serializers.ListField):
	child = serializers.IntegerField(min_value=1)


class PropertyGroupMemberCreateSerializer(serializers.ModelSerializer):
	r"""
	A serializer class we use for adding properties to groups;
	"""
	properties = PropertiesListField(allow_null=False, allow_empty=False, required=True)

	class Meta:
		model = PropertyGroupMembership
		fields = [
			"id",
			"group",
			"properties",
			"created_at",
			"updated_at"
		]
		read_only_fields = [
			"id",
			"group",
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
			raise serializers.ValidationError("Properties with given ids do not exist.")
		if PropertyGroupMembership.objects.all().filter(
				premises_id__in=properties_input,
				group_id=self.context['group_id']).exists():
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
			if not (current_user and current_user.can_add_to_group):
				raise exceptions.PermissionDenied
		# finally we check if the user has permissions to add properties
		# to the group
		if not UserGroupMembership.objects.all().filter(
				user=self.context["request"].user,
				group_id=self.context['group_id'],
				can_add_properties=True
		).exists():
			raise exceptions.PermissionDenied

		if properties_input:
			properties_instance = [
				PropertyGroupMembership(
					group_id=self.context['group_id'], premises_id=premises,
					added_by=self.context['request'].user
				)
				for premises in properties_input]
			properties = PropertyGroupMembership.objects.bulk_create(properties_instance)

		return properties
