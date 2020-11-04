from django.contrib.auth import get_user_model
from rest_framework import serializers


# TODO: make username generated from email and separate them
# TODO: customize login response for the one in the docs
#
#
#
#
#
#
#
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer class for creating a user (when registered)
    Author: Y. Borodin
    Version: 0.0.1
    Last update: 23.10.2020
    """
    password = serializers.CharField(write_only=True, required=True, style={
                                     "input_type": "password"})
    password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True, label="Confirm password")
    email = serializers.CharField(write_only=True, required=True, style={
        "input_type": "email"})
    first_name = serializers.CharField(write_only=True, required=True, style={
        "input_type": "name"})
    last_name = serializers.CharField(write_only=True, required=True, style={
        "input_type": "surname"})

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "password2",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """
        Explicitly created method. See docs on serializers in DRF
        :param: validated_data
        :return: user instance
        """
        email = validated_data["email"]
        password = validated_data["password"]
        password2 = validated_data["password2"]
        first_name = validated_data["first_name"]
        last_name = validated_data["last_name"]
        if email and User.objects.filter(username=email).exists():
            raise serializers.ValidationError(
                {"email": "User with given email already exists."})
        if password != password2:
            raise serializers.ValidationError(
                {"password": "The two passwords differ."})
        user = User(username=email, email=email, first_name=first_name,
                    last_name=last_name)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=True, style={
        "input_type": "username"})
    password = serializers.CharField(write_only=True, required=True, style={
        "input_type": "password"})

    class Meta:
        model = User
        fields = [
            "username",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data["password"]
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"email": "User with given email does not exist."})
        user = User.objects.get(username=username)
        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Invalid password"})
        return user
