from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from jwt import decode as jwt_decode
from django.conf import settings

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Get the token from the Authorization header
        auth = JWTAuthentication()
        try:
            auth_result = auth.authenticate(request)
            if auth_result:
                user, token = auth_result
                payload = jwt_decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                return payload.get('role') == 'admin'
        except:
            pass

        # Fallback to checking user flags
        return request.user.is_superuser or request.user.is_staff

class IsRegularUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Get the token from the Authorization header
        auth = JWTAuthentication()
        try:
            auth_result = auth.authenticate(request)
            if auth_result:
                user, token = auth_result
                payload = jwt_decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                return payload.get('role') == 'user'
        except:
            pass

        # Fallback to checking user flags
        return not request.user.is_superuser and not request.user.is_staff
