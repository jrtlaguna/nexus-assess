from dj_rest_auth.views import UserDetailsView as DjRestUserDetailsView
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User

from .serializers import UserSerializer


class UserDetailsView(DjRestUserDetailsView):
    serializer_class = UserSerializer


class DeactivateUserView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        user.is_active = False
        user.save()

        # Invalidate token
        Token.objects.filter(user=user).delete()

        return Response(
            {"message": "User account deactivated successfully."},
            status=status.HTTP_200_OK,
        )
