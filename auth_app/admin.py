from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (User, Role, BusinessElement,
    AccessRoleRule, UserRoles, Session)
# Register your models here.

class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'created_at'
        )
    list_filter = (
        'is_active',
        'is_staff',
        'created_at'
    )
    search_fields = [
        'email',
        'first_name',
        'last_name'
    ]
    ordering = ['-created_at']
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональные данные', {
            'fields': ('first_name', 'last_name', 'middle_name')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff')
        }),
        ('Важные даты', {
            'fields': ('last_login', 'created_at', 'updated_at', 'deleted_at')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'middle_name',
                        'password1', 'password2', 'is_active', 'is_staff')
        }),
    )

    readonly_fields = ['last_login', 'created_at', 'updated_at']

class SessionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'created_at',
        'expires_at',
        'is_active'
    )
    list_filter = (
        'is_active',
        'created_at'
    )
    search_fields = [
        'user__email'
    ]
    readonly_fields = [
        'id',
        'token',
        'created_at'
    ]

    def has_add_permission(self, request):
        return False
    
class BusinessElementAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'element_type',
        'created_at'
    )
    list_filter = (
        'element_type',
        'created_at'
    )
    search_fields = [
        'name',
        'description'
    ]
    readonly_fields = [
        'id',
        'created_at'
    ]

class RoleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_default',
        'created_at'
    )
    list_filter = (
        'is_default',
        'created_at'
    )
    search_fields = [
        'name',
        'description'
    ]
    readonly_fields = [
        'id',
        'created_at'
    ]
    # filter_horizontal = []

class AccessRoleRuleAdmin(admin.ModelAdmin):
    list_display = (
        'role', 'element',
        'read_permission', 'read_all_permission',
        'create_permission', 
        'update_permission', 
        'delete_permission', 
    )
    list_filter = (
        'role',
        'element'
    )
    search_fields = [
        'role__name',
        'element__name'
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at'
    ]

class UserRolesAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'role',
        'assigned_by',
        'assigned_at'
    )
    list_filter = (
        'role',
        'assigned_at'
    )
    search_fields = [
        'user__email',
        'role__name'
    ]
    readonly_fields = [
        'id',
        'assigned_at'
    ]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(User, UserAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(BusinessElement, BusinessElementAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(AccessRoleRule, AccessRoleRuleAdmin)
admin.site.register(UserRoles, UserRolesAdmin)

admin.site.site_header = 'Система аутентификации и авторизации'
admin.site.site_title = 'Администрирование системы'
admin.site.index_title = 'Администрирование системы'