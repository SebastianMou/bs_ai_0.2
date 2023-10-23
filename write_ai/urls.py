from django.urls import path
from django.contrib.auth import views as auth_views

from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('main/', views.main, name='main'),
    path('chat/', views.chat, name='chat'),
    path('img_gen/', views.img_gen, name='img_gen'),
    path('tasks/', views.tasks, name='tasks'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('login_with_email/', views.login_with_email, name='login_with_email'),
    path('register/', views.user_register, name='user_register'),

    # Tasks
    path('tasks/', views.tasks, name='tasks'),
    path('items/', views.update_task_order, name='update_task_order'),
    path('items_detail/<int:pk>/', views.items_detail, name='items_detail'),
    path('create_task/', views.create_task, name='create_task'),
    path('delete_task/<int:pk>/', views.delete_task, name='delete_task'),
    path('edit_task/<int:pk>/', views.edit_task, name='edit_task'),

    # Docuemtns
    path('ai_documents/', views.ai_documents, name='ai_documents'),
    path('create_document/', views.create_document, name='create_document'),
    path('edit_document/<int:pk>/', views.edit_document, name='edit_document'),
    path('view_document/<int:pk>/', views.view_document, name='view_document'),

    # Forgoten password
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'), name="password_reset"),
    path('password_reset_sent/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="auth/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),

    # activación de la cuenta de usuario por correo electrónico
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('sending_activate_token/', views.sending_activate_token, name='sending_activate_token'),

    path('public_privacy_policy/', views.public_privacy_policy, name='public_privacy_policy'), 
    path('public_terms_of_service/', views.public_terms_of_service, name='public_terms_of_service'), 
]