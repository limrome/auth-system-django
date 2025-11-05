import jwt
from django.conf import settings
from django.utils import timezone
from .models import Session, User

class CustomAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = self.authenticate_user(request)
        response = self.get_response(request)
        return response
    
    def authenticate_user(self, request):
        user = None
        user = self.authenticate_by_token(request)
        if user:
            return user
        
        user = self.authenticate_by_session(request)
        if user:
            return user
        
        return None
    
    def authenticate_by_token(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        try:
            token = auth_header.split(' ')[1]

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            
            if not user_id:
                return None
            
            session = Session.objects.filter(
                user_id=user_id,
                token=token,
                is_active=True,
                expires_at__gt=timezone.now()
            ).first()

            if session:
                user = User.objects.get(id=user_id, is_active=True)
                return user
            
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            pass

        return None
    
    def authenticate_by_session(self, request):
        session_id = request.COOKIES.get('session_id')
        if not session_id:
            return None

        try:
            session = Session.objects.get(
                id=session_id, 
                is_active=True,
                expires_at__gt=timezone.now()
                )
            return session.user
        except (Session.DoesNotExist, ValueError):
            return None
