from rest_framework import permissions
from .models import AccessRoleRule, UserRoles, BusinessElement

class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if self._is_public_endpoint(request):
            return True
        if not request.user or not request.user.is_authenticated:
            return False
           
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            return True

        element_type = getattr(view, 'business_element_type', None)
        action = self._get_action_from_method(request.method)

        if not element_type:
            return True
        
        return self._check_resource_access(request.user, element_type, action)
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if hasattr(request.user, 'is_staff') and request.user.is_staff:
            return True

        element_type = getattr(view, 'business_element_type', None)
        action = self._get_action_from_method(request.method)

        if not element_type:
            return True
        
        return self._check_object_access(request.user, element_type, action, obj)
    
    def _is_public_endpoint(self, view):
        public_views = ['RegisterView', 'LoginView']

        return view.__class__.__name__ in public_views
    
    def _get_action_from_method(self, method):
        method_to_action = {
            'GET': 'read',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete'
        }
        return method_to_action.get(method, 'read')
    
    def _check_resource_access(self, user, element_type, action):
        try:
            element = BusinessElement.objects.get(element_type=element_type)
            user_roles = UserRoles.objects.filter(user=user)

            for user_role in user_roles:
                rule = AccessRoleRule.objects.filter(
                    role=user_role.role,
                    element=element
                ).first()

                if rule and self._has_permission_for_action(rule, action):
                    return True

        except BusinessElement.DoesNotExist:
            return True

        return False
    
    def _check_object_access(self, user, element_type, action, obj):
        try:
            element = BusinessElement.objects.get(element_type=element_type)
            user_roles = UserRoles.objects.filter(user=user)

            for user_role in user_roles:
                rule = AccessRoleRule.objects.filter(
                    role=user_role.role,
                    element=element
                ).first()

                if rule:
                    is_owner = self._is_object_owner(obj, user)
                    if self._has_object_permission_for_action(rule, action, is_owner):
                        return True

        except BusinessElement.DoesNotExist:
            return True

        return False
    
    def _has_permission_for_action(self, rule, action):
        permission_map = {
            'read': ['read_permission', 'read_all_permission'],
            'create': ['create_permission'],
            'update': ['update_permission'],
            'delete': ['delete_permission']
        }
        permissions = permission_map.get(action, [])

        return any(
            getattr(rule, perm, False)
            for perm in permissions
        )
    
    def _has_object_permission_for_action(self, rule, action, is_owner):
        if action == 'read':
            return rule.read_all_permission or (rule.read_permission and is_owner)
        elif action == 'update':
            return rule.update_permission and is_owner
        elif action == 'delete':
            return rule.delete_permission and is_owner
        elif action == 'create':
            return rule.create_permission
        
        return False
    
    def _is_object_owner(self, obj, user):
        owner_field = ['owner', 'user', 'created_by', 'author']

        for field in owner_field:
            if hasattr(obj, field):
                owner = getattr(obj, field)
                if hasattr(owner, 'id'):
                    return owner.id == user.id 
                else:
                    return owner == user.id
                
        return False
    
class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )
    
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        owner_fields = ['owner', 'user', 'created_by']
        for field in owner_fields:
            if hasattr(obj, field):
                owner = getattr(obj, field)
                if hasattr(owner, 'id'):
                    return owner.id == request.user.id
                else:
                    return owner == request.user.id
                
        return False