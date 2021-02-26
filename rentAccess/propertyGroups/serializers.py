from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import PropertyGroup, PropertyGroupMembership, UserGroupMembership

User = get_user_model()


class GroupMemberCreateSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(required=True)

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
		email = validated_data.get("email")
		try:
			user = User.objects.get(email=email)
		except User.DoesNotExist:
			raise serializers.ValidationError({
				"user: user with given email does not exist."
			})
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

		member = UserGroupMembership(
			user=user,
			group_id=group_id,
			is_creator=True,
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

	class Meta:
		model = PropertyGroup
		fields = [
			"title",
			"descriptions",
			"created_at",
			"updated_at"
		]
		read_only_fields = [
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
