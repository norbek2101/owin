from django.urls import path
from .views import ClientListCreateView, ClientDetailView, ProposalListCreateView, ProposalDetailView

app_name = 'proposals'

urlpatterns = [
    path('clients/', ClientListCreateView.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('proposals/', ProposalListCreateView.as_view(), name='proposal-list-create'),
    path('proposals/<int:pk>/', ProposalDetailView.as_view(), name='proposal-detail'),
]