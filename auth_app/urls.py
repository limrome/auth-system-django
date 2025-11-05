from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'auth_app'

router = DefaultRouter()
router.register('admin/roles', views.RoleViewSet, basename='role')
router.register('admin/business-elements', views.BusinessElementViewSet, basename='business-element')
router.register('admin/access-rules', views.AccessRoleRuleViewSet, basename='access-rule')
router.register('admin/user-roles', views.UserRoleViewSet, basename='user-role')
router.register('admin/sessions', views.SessionViewSet, basename='session')


urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/profile/', views.UserProfileView.as_view(), name='profile'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change-password'),

    path('products/', views.ProductView.as_view(), name='products'),
    path('orders/', views.OrderView.as_view(), name='orders'),
    path('users/', views.UserManagementView.as_view(), name='user-management'),

    path('', include(router.urls)),
]

