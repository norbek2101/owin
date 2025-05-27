from rest_framework import serializers
from .models import Client, Proposal
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone_number']

class ClientSerializer(serializers.ModelSerializer):
    added_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Client
        fields = ['id', 'company_name', 'address', 'phone_number', 'email', 'added_by', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """
        Ensure at least one contact field is provided.
        """
        if not data.get('phone_number') and not data.get('email'):
            raise serializers.ValidationError("Either phone_number or email must be provided.")
        return data

    def create(self, validated_data):
        """
        Set the added_by field to the current user.
        """
        request = self.context.get('request')
        validated_data['added_by'] = request.user
        return super().create(validated_data)

class ProposalSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), source='client', write_only=True
    )
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Proposal
        fields = ['id', 'client', 'client_id', 'title', 'description', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        """
        Set the created_by field to the current user.
        """
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        return super().create(validated_data)