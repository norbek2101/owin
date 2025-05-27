from rest_framework import generics, permissions
from proposals.models import Client, Proposal
from proposals.serializers import ClientSerializer, ProposalSerializer

class ClientListCreateView(generics.ListCreateAPIView):
    """
    List all clients or create a new client.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return only clients added by the current user.
        """
        return self.queryset.filter(added_by=self.request.user)

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a client.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Restrict to clients added by the current user.
        """
        return self.queryset.filter(added_by=self.request.user)

class ProposalListCreateView(generics.ListCreateAPIView):
    """
    List all proposals or create a new proposal.
    """
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return only proposals created by the current user.
        """
        return self.queryset.filter(created_by=self.request.user)

class ProposalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a proposal.
    """
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Restrict to proposals created by the current user.
        """
        return self.queryset.filter(created_by=self.request.user)