from django.urls import path
from . import views

app_name = 'user_accounts'

urlpatterns = [
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('register_user/', views.register_user, name='register_user'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]
