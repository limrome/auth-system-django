import uuid
import bcrypt
import jwt

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
# Create your models here.

# Менеджер пользователей
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен для заполнения')
        email = self.normalize_email(email)
        extra_fields.pop('is_superuser', None)
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        
        extra_fields.pop('is_superuser', None)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        return self.create_user(email, password, **extra_fields)
    

# Пользователь
class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name='email')
    first_name = models.CharField(max_length=30, verbose_name='Имя') 
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=30, verbose_name='Отчество', blank=True)

    is_active = models.BooleanField(default=True, verbose_name='Активен') 
    is_staff = models.BooleanField(default=False, verbose_name='Сотрудник')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    deleted_at = models.DateTimeField(null=True, verbose_name='Дата удаления', blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def set_password(self, raw_password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
        self.password = hashed_password.decode('utf-8')   

    def check_password(self, raw_password):
        try:
            return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))          
        except (ValueError, AttributeError):
            return False
        
    def delete(self, soft_delete=True, *args, **kwargs):
        if soft_delete:
            self.is_active = False
            self.deleted_at = timezone.now()
            self.save()
        else:
            super().delete(*args, **kwargs)

# Сессия
class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    token = models.TextField(verbose_name='Токен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    expires_at = models.DateTimeField(verbose_name='Дата истечения')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta: 
        db_table = 'sessions'
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'
        ordering = ['-created_at']

    def __str__(self):
        return f"Сессия {self.user.email} ({self.created_at})"
    
    def is_expired(self):
        return self.expires_at < timezone.now()
    
# Бизнес-элемент
class BusinessElement(models.Model):
    ELEMENT_TYPES = (
        ('user', 'Пользователи'),
        ('product', 'Товары'),
        ('order', 'Заказы'),
        ('shop', 'Магазины'),
        ('access_rule', 'Правила доступа'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Название')
    element_type = models.CharField(
        max_length=20,
        choices=ELEMENT_TYPES,
        verbose_name='Тип элемента'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        db_table = 'business_elements'
        verbose_name = 'Бизнес-элемент'
        verbose_name_plural = 'Бизнес-элементы'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_element_type_display()})"
    
# Роль
class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, verbose_name='Название роли')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_default = models.BooleanField(default=False, verbose_name='Ролб по умолчанию')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:                         
        db_table = 'roles'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
# Правило доступа
class AccessRoleRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='Роль')
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, verbose_name='Бизнес-элемент')

    read_permission = models.BooleanField(default=False, verbose_name='Чтение своих')
    read_all_permission = models.BooleanField(default=False, verbose_name='Чтение всех')
    create_permission = models.BooleanField(default=False, verbose_name='Создание')
    update_permission = models.BooleanField(default=False, verbose_name='Обновление своих')
    # update_all_permission = models.BooleanField(default=False, verbose_name='Обновление всех')
    delete_permission = models.BooleanField(default=False, verbose_name='Удаление своих')
    # delete_all_permission = models.BooleanField(default=False, verbose_name='Удаление всех')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:                         
        db_table = 'access_role_rules'
        verbose_name = 'Правило доступа роли'
        verbose_name_plural = 'Правила доступа ролей'
        unique_together = ['role', 'element']
        ordering = ['role', 'element']

    def __str__(self):
        return f"{self.role.name} - {self.element.name}"
    
# Связь пользователь-роль
class UserRoles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='Роль')
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата назначения')
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_roles',
        verbose_name='Назначил'
    )

    class Meta:                         
        db_table = 'user_roles'
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        unique_together = ['user', 'role']
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"