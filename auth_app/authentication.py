import jwt
from django.conf import settings
from django.utils import timezone
from .models import Session, User
from datetime import datetime, timedelta
from rest_framework import exceptions, authentication

class CustomTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None

        try:
            token = auth_header.split(' ')[1]

            return self.authenticate_credentials(token)
        except (IndexError, ValueError):
            raise exceptions.AuthenticationFailed('Неверный формат токена')
        
    def authenticate_credentials(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']

            if not user_id:
                raise exceptions.AuthenticationFailed('Пользователь не найден')
            
            session = Session.objects.filter(
                user_id=user_id,
                token=token,
                is_active=True,
                expires_at__gt=timezone.now()
            ).first()

            if not session:
                raise exceptions.AuthenticationFailed('Сессия истекла')
            
            user = User.objects.get(id=user_id, is_active=True)
            return user, token
        
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Сессия истекла')
        
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Неверный токен')
        
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Пользователь не найден')

    @staticmethod
    def generate_token(user):
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def create_session(user, token):
        expires_at = timezone.now() + timedelta(days=7)

        session = Session.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )      
        return session                              