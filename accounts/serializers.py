from rest_framework import serializers
from .models import Client, Proposal

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'phone', 'created_at']


class ProposalSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)

    class Meta:
        model = Proposal
        fields = ['id', 'client', 'title', 'description', 'amount', 'created_at', 'submitted_at']

