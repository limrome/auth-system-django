from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from auth_app.models import Role, BusinessElement, AccessRoleRule, UserRoles, Session
from django.utils import timezone
from datetime import timedelta

User = get_user_model()
class Command(BaseCommand):
    def handle(self, *args, **options):
        
        self.stdout.write('Создание бизнес-элементов')
        elements_data = [
            ('Пользователи', 'user', 'Управдение пользователями системы'),
            ('Товары', 'product', 'Управление товарами'),
            ('Заказы', 'order', 'Управление заказами'),
            ('Магазины', 'shop', 'Управление магазинами'),
            ('Правила доступа', 'access_rule', 'Управление правилами доступа'),
        ]
        elements = {}
        for name, element_type, description in elements_data:
            element, created = BusinessElement.objects.get_or_create(
                name=name,
                element_type=element_type,
                defaults={
                    'description': description
                }
            )
            elements[element_type] = element
            if created:
                self.stdout.write(f'Создан бизнес-элемент {name}')
            else:
                self.stdout.write(f'Бизнес-элемент {name} уже существует')

        self.stdout.write('Создание ролей')
        roles_data = [
            ('admin', 'Администратор системы', True),
            ('manager', 'Менеджер', False),
            ('user', 'Пользователь', True),
            ('guest', 'Гость', False),
        ]
        roles = {}
        for name, description, is_default in roles_data:
            role, created = Role.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'is_default': is_default,
                }
            )
            roles[name] = role
            if created:
                self.stdout.write(f'Создана роль {name}')
            else:
                self.stdout.write(f'Роль {name} уже существует')

        self.stdout.write('Создание правил доступа')
        # роль, элемент, read, read_all, create, update, delete
        rules_data = [
            ('admin', 'user', True, True, True, True, True),
            ('admin', 'product', True, True, True, True, True),
            ('admin', 'order', True, True, True, True, True),
            ('admin', 'shop', True, True, True, True, True),
            ('admin', 'access_rule', True, True, True, True, True),
            
            ('manager', 'user', True, True, False, False, False),
            ('manager', 'product', True, True, True, True, False),
            ('manager', 'order', True, True, True, True, False),
            ('manager', 'shop', True, True, True, True, False),
            ('manager', 'access_rule', False, False, False, False, False),
            
            ('user', 'user', True, False, False, True, False),
            ('user', 'product', True, True, True, True, True),
            ('user', 'order', True, False, True, True, True),
            ('user', 'shop', True, True, False, False, False),
            ('user', 'access_rule', False, False, False, False, False),
            
            ('guest', 'user', False, False, False, False, False),
            ('guest', 'product', False, True, False, False, False),
            ('guest', 'order', False, False, False, False, False),
            ('guest', 'shop', False, True, False, False, False),
            ('guest', 'access_rule', False, False, False, False, False),
        ]
        for role_name, element_type, read, read_all, create, update, delete in rules_data:
            rule, created = AccessRoleRule.objects.get_or_create(
                role=roles[role_name],
                element=elements[element_type],
                defaults={
                    'read_permission': read,
                    'read_all_permission': read_all,
                    'create_permission': create,
                    'update_permission': update,
                    'delete_permission': delete,
                }   
            )
            if created:
                self.stdout.write(f'Создано правило доступа для роли {role_name} и бизнес-элемента {element_type}')
            else:
                self.stdout.write(f'Правило доступа для роли {role_name} и бизнес-элемента {element_type} уже существует')

        self.stdout.write('Создание пользователей')
        users_data = [
            ('admin@example.com', 'Админ', 'Системы', 'admin123', True, True, 'admin'),
            ('manager@example.com', 'Менеджер', 'Отдела', 'manager123', True, False, 'manager'),
            ('user@example.com', 'Иван', 'Петров', 'user123', True, False, 'user'),
            ('guest@example.com', 'Гость', 'Тестовый', 'guest123', True, False, 'guest'),
        ]
        for email, first_name, last_name, password, is_active, is_staff, role_name in users_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': is_active,
                    'is_staff': is_staff,
                }
            )
                
            if created:
                user.set_password(password)
                user.save()

                UserRoles.objects.create(user=user, role=roles[role_name])
                self.stdout.write(f'Создан пользователь {email} с ролью {role_name}')
            else:
                self.stdout.write(f'Пользователь {email} уже существует')

        self.stdout.write('Создание сессий')
        admin_user = User.objects.get(email='admin@example.com')
        from auth_app.authentication import CustomTokenAuthentication
        token = CustomTokenAuthentication.generate_token(admin_user)
        session, created = Session.objects.get_or_create(
            user=admin_user, 
            defaults={
                'token': token,
                'expires_at': timezone.now() + timedelta(days=7),
                'is_active': True,
            }
        )

        if created:
            self.stdout.write(f'Создана сессия для администратора')
            self.stdout.write(f'Токен: {token}')