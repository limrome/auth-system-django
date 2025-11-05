from rest_framework import serializers
from .models import User, Session, Role, UserRoles, BusinessElement, AccessRoleRule

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        label='Пароль'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        label='Подтверждение пароля'
    )

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'middle_name',
            'password',
            'password_confirm'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}     
        } 

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)
        if password != password_confirm:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        user = User.objects.create_user(**validated_data)
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email', 
            'first_name', 
            'last_name', 
            'middle_name',
            'created_at',
            'updated_at'
            ]
        read_only_fields = ['id', 'email','created_at', 'updated_at']

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, label='Электронная почта')
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        label='Пароль'
    )
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if not email or not password:
            raise serializers.ValidationError('Email и пароль обязательны')
        
        return attrs
    
class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = [
            'id', 
            'name', 
            'element_type',
            'description',
            'created_at'
            ]
        read_only_fields = ['id', 'created_at']

class AccessRoleRuleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    element_name = serializers.CharField(source='element.name', read_only=True)
    class Meta:
        model = AccessRoleRule
        fields = [
            'id',
            'role',
            'role_name',
            'element', 
            'element_name',
            'read_permission',
            'read_all_permission', 
            'create_permission',
            'update_permission',
            'delete_permission',
            'created_at',
            'updated_at'
            ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class RoleSerializer(serializers.ModelSerializer):
    rules = AccessRoleRuleSerializer(
        source='accessrolerule_set', 
        many=True, 
        read_only=True
        )
    user_count = serializers.SerializerMethodField()
    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'description',
            'is_default',
            'user_count',
            'rules',
            'created_at'
            ]
        read_only_fields = ['id', 'created_at']

    def get_user_count(self, obj):
        return UserRoles.objects.filter(role=obj).count()
    
class UserRolesSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    role_name = serializers.CharField(source='role.name', read_only=True)
    class Meta:
        model = UserRoles
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'role',
            'role_name',
            'assigned_at',
            'assigned_by'
            ]
        read_only_fields = ['id', 'assigned_at']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    
class SessionSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = Session
        fields = [
            'id',
            'user',
            'user_email',
            'created_at',
            'expires_at',
            'is_active'
            ]
        read_only_fields = ['id', 'created_at']
    
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        required=True, 
        style={'input_type': 'password'},
        label='Старый пароль'
    )
    new_password = serializers.CharField(
        required=True, 
        min_length=8,
        style={'input_type': 'password'},
        label='Новый пароль'
    )
    new_password_confirm = serializers.CharField(
        required=True, 
        style={'input_type': 'password'},
        label='Подтверждение нового пароля'
    )
    
    def validate(self, attrs):
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError(
                'Новые пароли не совпадают'
            )
        
        return attrs