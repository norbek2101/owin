from rest_framework import serializers
from django.db import IntegrityError
from .models import User
from phonenumber_field.serializerfields import PhoneNumberField

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    phone_number = PhoneNumberField(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['name', 'phone_number', 'email', 'password']

    def validate(self, data):
        if not data.get('phone_number') and not data.get('email'):
            raise serializers.ValidationError("Either phone_number or email must be provided")
        return data

    def create(self, validated_data):
        try:
            return User.objects.create_user(**validated_data)
        except IntegrityError as e:
            if 'email' in str(e):
                raise serializers.ValidationError({"email": "A user with that email already exists."})
            if 'phone_number' in str(e):
                raise serializers.ValidationError({"phone_number": "A user with that phone number already exists."})
            raise e
            # raise serializers.ValidationError({"non_field_errors": "An unexpected error occurred during user creation."})

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)