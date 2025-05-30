from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get_by_identifier(username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None