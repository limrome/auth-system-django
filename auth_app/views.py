from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView


from .models import User, Role, BusinessElement, AccessRoleRule, UserRoles, Session
from .serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer,
    UserLoginSerializer,
    RoleSerializer,
    BusinessElementSerializer,
    AccessRoleRuleSerializer,
    UserRolesSerializer,
    SessionSerializer,
    PasswordChangeSerializer
)
from .authentication import CustomTokenAuthentication
from .permissions import CustomPermission, IsAdminUser

# Create your views here.
# Регитсрация нового пользователя
class RegisterView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user =serializer.save()
            default_role = Role.objects.filter(is_default=True).first()
            if default_role:
                UserRoles.objects.create(user=user, role=default_role)
            return Response({'message': 'Пользователь успешно зарегистрирован',
                            'user_id': str(user.id)
                            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Вход в систему
class LoginView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': 'Неверный пароль'}, status=status.HTTP_401_UNAUTHORIZED)

        token = CustomTokenAuthentication.generate_token(user)
        session = CustomTokenAuthentication.create_session(user, token)
        user_data = UserProfileSerializer(user).data

        response = Response({
            'message': 'Успешная авторизация',
            'user': user_data,
            'token': token
        })

        response.set_cookie(
            key='session_id', 
            value=str(session.id), 
            expires=session.expires_at,
            httponly=True,
            secure=False,
            samesite='Lax'
            )
        return response

# Выход из системы  
class LogoutView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def post(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            Session.objects.filter(token=token, is_active=True).update(is_active=False)

        session_id = request.COOKIES.get('sessionid')
        if session_id:
            Session.objects.filter(id=session_id).update(is_active=False)

        response = Response({'message': 'Вы успешно вышли из системы'})
        response.delete_cookie('sessionid')
        return response
    
# Управление профилем
class UserProfileView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserProfileSerializer(
            request.user, 
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Изменение пароля
class ChangePasswordView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        if not user.check_password(old_password):
            return Response({'error': 'Неверный текущий пароль'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            current_token = auth_header.split(' ')[1]
            Session.objects.filter(
                user=user,
                is_active=True
            ).exclude(
                token=current_token
            ).update(is_active=False)

        return Response({'message': 'Пароль успешно изменен'})
    

# Mock API для товаров
class ProductView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]
    business_element_type = 'product'

    def get(self, request):
        products = [
            {
                'id': 1,
                'name': 'Продукт 1',
                'price': 89990,
                'owner_id': str(request.user.id),
                'created_by': str(request.user.id)
            },
            {
                'id': 2,
                'name': 'Продукт 2',
                'price': 99990,
                'owner_id': 'other-user-id',
                'created_by': 'other-user-id'
            },
            {
                'id': 3,
                'name': 'Продукт 3',
                'price': 109990,
                'owner_id': str(request.user.id),
                'created_by': str(request.user.id)
            }

        ]
        return Response({
            'count': len(products),
            'results': products
        })
    
    def post(self, request):
        return Response({
            'message': 'Товар успешно создан',
            'product_id': 123,
            'name': request.data.get('name', 'Новый товар')            
        }, status=status.HTTP_201_CREATED)
    
# Mock API для заказов
class OrderView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]
    business_element_type = 'order'

    def get(self, request):
        orders = [
            {
                'id': 1,
                'product': 'Продукт 1',
                'status':'доставлен',
                'total_amount': 89990,
                'owner_id': str(request.user.id),
                'created_by': str(request.user.id)
            },
            {
                'id': 2,
                'product': 'Продукт 2',
                'status':'в обработке',
                'total_amount': 99990,
                'owner_id': 'other-user-id', 
                'created_by': 'other-user-id'
            },
        ]
        return Response({
            'count': len(orders),
            'results': orders
        })
    
    def post(self, request):
        return Response({
            'message': 'Заказ успешно создан',
            'order_id': 456,
            'status': 'в обработке'            
        }, status=status.HTTP_201_CREATED)
    
# Mock API для управления пользователями
class UserManagementView(APIView):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [CustomPermission]
    business_element_type = 'user'

    def get(self, request):
        users_data = [
            {
                'id': str(request.user.id),
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'is_active': True
            },
            {
                'id': 'other-user-uuid',
                'email': 'other@example.com',
                'first_name': 'Другой',
                'last_name': 'Пользователь',
                'is_active': True
            }
        ]

        return Response({
            'count': len(users_data),
            'results': users_data
        })
    
# API для управления ролями
class RoleViewSet(viewsets.ModelViewSet):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def perform_create(self, serializer):
        role = serializer.save()
        permission_data = self.request.data.get('permissions', [])
        if permission_data:
            pass

# API для управления бизнес-элементами
class BusinessElementViewSet(viewsets.ModelViewSet):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAdminUser]
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer

# API для управления правами доступа
class AccessRoleRuleViewSet(viewsets.ModelViewSet):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAdminUser]
    queryset = AccessRoleRule.objects.all()
    serializer_class = AccessRoleRuleSerializer

# API для управления ролями пользователя
class UserRoleViewSet(viewsets.ModelViewSet):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAdminUser]
    queryset = UserRoles.objects.all()
    serializer_class = UserRolesSerializer

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

# API для управления сессиями
class SessionViewSet(viewsets.ModelViewSet):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        session = self.get_object()
        session.is_active = False
        session.save()
        return Response({'message': 'Сессия успешно деактивирована'})
    
    @action(detail=False, methods=['post'])
    def deactivate_all_user_sessions(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({
                'error': 'user_id обязательное поле'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        sessions = Session.objects.filter(user_id = user_id, is_active=True)
        count = sessions.update(is_active=False)
        return Response({
            'message': f"Деактивировано {count} сессий пользователя {user_id}"
        })