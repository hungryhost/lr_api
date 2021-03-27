from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from .models import (CustomUser, UserImage,
                     Document, DocumentType, AddressType,
                     BillingAddress, MetaBannedInfo, ClientPlan, KYCOperation, PlannedClient, PlanRequests)
from .models import Phone, PhoneType

# Register your models here.
admin.site.register(UserImage)

admin.site.register(PhoneType)
admin.site.register(Phone)
admin.site.register(DocumentType)
admin.site.register(Document)
admin.site.register(AddressType)
admin.site.register(BillingAddress)


class UserCreationForm(forms.ModelForm):
	"""A form for creating new users. Includes all the required
	fields, plus a repeated password."""
	password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

	class Meta:
		model = CustomUser
		fields = (
			'email',
			'first_name',
			'last_name',
			'middle_name',
			'bio',
			'dob',
			'gender'
		)

	def clean_password2(self):
		# Check that the two password entries match
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise ValidationError("Passwords don't match")
		return password2

	def save(self, commit=True):
		# Save the provided password in hashed format
		user = super().save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user


class UserChangeForm(forms.ModelForm):
	"""A form for updating users. Includes all the fields on
	the user, but replaces the password field with admin's
	password hash display field.
	"""
	password = ReadOnlyPasswordHashField()

	class Meta:
		model = CustomUser
		fields = (
			'first_name',
			'work_email',
			'middle_name',
			'phone',
			'last_name',
			'bio',
			'email_confirmed',
			'phone_confirmed',
			'dob',
			'gender',
			'timezone',
			'two_factor_auth',
			'client_rating',
			'is_banned',
			'use_work_email_incbookings',
			'use_work_email_outbookings',
			'show_work_email_in_contact_info',
			'show_main_email_in_contact_info',
			'additional_info',
			'tos_version',
			'is_active',
			'is_admin',
			'is_staff',
			'is_superuser'
		)

	def clean_password(self):
		# Regardless of what the user provides, return the initial value.
		# This is done here, rather than on the field, because the
		# field does not have access to the initial value
		return self.initial["password"]


class InlineKYC(admin.TabularInline):
	model = KYCOperation


class InlinePlan(admin.TabularInline):
	model = PlannedClient


class UserAdmin(BaseUserAdmin):
	# The forms to add and change user instances

	inlines = [InlineKYC, ]
	list_display = ['totol_tagged_article',]

	def totol_tagged_article(self, obj):
		return obj.kyc_info.all().filter(user=obj)

	form = UserChangeForm
	add_form = UserCreationForm
	readonly_fields = (
		'last_password_update',
		'created_at',
		'updated_at',
	)
	# The fields to be used in displaying the User model.
	# These override the definitions on the base UserAdmin
	# that reference specific fields on auth.User.
	list_display = (
		'email',
		'first_name',
		'last_name',
		'is_admin',
		'is_staff',
	)
	# list_filter = ('is_admin',)
	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		('Personal info', {'fields': (
			'first_name',
			'last_name',
			'middle_name',
			'work_email',
			'phone',
			'bio',
			'dob',
			'gender',
			'timezone',
			'use_work_email_incbookings',
			'use_work_email_outbookings',
			'show_work_email_in_contact_info',
			'show_main_email_in_contact_info',

		)}),
		('Internal Info', {'fields': (
			'email_confirmed',
			'phone_confirmed',
			'two_factor_auth',
			'client_rating',
			'is_banned',
			'additional_info',
			'last_password_update',
			'tos_version',
			'created_at',
			'updated_at',

		)}),
		('Permissions', {
			'fields': ('is_active', 'is_staff', 'is_admin', 'is_superuser', 'groups'),
		}),
		#('Related Entities', {
		#	'fields': ('user__user_plans', 'user__user_plan_requests', 'user__kyc_info', 'user__account_images',),
		#}),
	)
	# add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
	# overrides get_fieldsets to use this attribute when creating a user.
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'dob', 'password1', 'password2'),
		}),
	)
	search_fields = ('email',)
	ordering = ('email',)
	#filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(CustomUser, UserAdmin)
admin.site.register(MetaBannedInfo)
admin.site.register(ClientPlan)
admin.site.register(PlannedClient)
admin.site.register(PlanRequests)
admin.site.register(KYCOperation)
#admin.site.unregister(Group)
