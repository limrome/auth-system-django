
## Модели данных

### Core Models
- **User** - пользователи (UUID, email, пароль bcrypt)
- **Session** - активные сессии с JWT токенами

### RBAC Models  
- **Role** - роли (`admin`, `manager`, `user`, `guest`)
- **BusinessElement** - бизнес-сущности (`users`, `products`, `orders`)
- **AccessRoleRule** - правила доступа (CRUD права)
- **UserRoles** - связь пользователей с ролями

## Матрица прав

| Право / Роль | Admin | Manager | User | Guest |
|--------------|----------|------------|---------|----------|
| **Чтение всех** | + | + | - | - |
| **Чтение своих** | + | - | + | - |
| **Создание** | + | + | + | - |
| **Обновление** | + | + | + | - |
| **Удаление** | + | - | - | - |

## Поток аутентификации/авторизации

1. **Запрос → Auth Middleware** (JWT/Session проверка)
2. **Request → Custom Permission** (определение прав)
3. **Business Element + Action → Access Rules** (проверка CRUD)
4. **Разрешение/Запрет** (200/401/403)

## Безопасность

- JWT токены (7 дней) + сессии в БД
- Bcrypt хеширование паролей  
- Мягкое удаление пользователей
- Проверка владения объектами

## Тестирование 

### Импортируйте файлы из папки docs/:
- docs/auth-system-postman-collection.json

- docs/auth-system-postman-environment.json