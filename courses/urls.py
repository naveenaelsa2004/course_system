from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('course/create/', views.course_create, name='course_create'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('course/<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<int:pk>/unenroll/', views.unenroll_course, name='unenroll_course'),
    path('course/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('course/<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('course/<int:pk>/students/', views.course_students, name='course_students'),
    path('users/manage/', views.manage_users, name='manage_users'),
    path('users/<int:pk>/approve/', views.approve_user, name='approve_user'),
    path('users/<int:pk>/delete/', views.delete_user, name='delete_user'),
    path('settings/', views.site_settings, name='site_settings'),
    path('pending-approval/', views.pending_approval, name='pending_approval'),
    path('course/<int:pk>/focus/', views.focus_studio, name='focus_studio'),
    path('users/instructor/add/', views.create_instructor, name='create_instructor'),
]
