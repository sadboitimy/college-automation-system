"""
URL configuration for college_automation_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from main import views
from django.contrib.auth import views as auth_views
from main.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'api/students', StudentViewSet)
router.register(r'api/teachers', TeacherViewSet)
router.register(r'api/groups', GroupViewSet)
router.register(r'api/subjects', SubjectViewSet)
router.register(r'api/schedule', ScheduleViewSet)
router.register(r'api/classrooms', ClassroomViewSet)
router.register(r'api/grades', GradeViewSet)
router.register(r'api/my', MyProfileViewSet, basename='myprofile')
router.register(r'api/admin/users', AdminCreateUserViewSet, basename='admin-users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    # Аутентификация
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/create-user/', admin_create_user, name='admin_create_user'),
    path('api/auth/', CustomAuthToken.as_view()),

    # Основные страницы
    path('students/', views.students_list, name='students_list'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    
    path('teachers/', views.teachers_list, name='teachers_list'),
    path('teachers/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),
    
    path('groups/', views.groups_list, name='groups_list'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),

    path('grades/', views.grades_view, name='grades_list'),
    path('grades/<int:grade_id>/', views.grade_detail, name='grade_detail'),
    
    path('subjects/', views.subjects_list, name='subjects_list'),
    path('subjects/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    
    path('classrooms/', views.classrooms_list, name='classrooms_list'),
    path('classrooms/<int:classroom_id>/', views.classroom_detail, name='classroom_detail'),

    path('schedule/', views.schedule_view, name='schedule'),
    path('schedule/<int:schedule_id>/', views.schedule_detail, name='schedule_detail'),
    path('schedule/<int:schedule_id>/attendance/', views.schedule_attendance, name='schedule_attendance'),

# ================= CRUD Операции =================

    # Студенты
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:student_id>/update/', views.student_update, name='student_update'),
    path('students/<int:student_id>/delete/', views.student_delete, name='student_delete'),
    
    # Преподаватели
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:teacher_id>/update/', views.teacher_update, name='teacher_update'),
    path('teachers/<int:teacher_id>/delete/', views.teacher_delete, name='teacher_delete'),
    
    # Группы
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:group_id>/update/', views.group_update, name='group_update'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    
    # Расписание
    path('schedule/create/', views.schedule_create, name='schedule_create'),
    path('schedule/<int:schedule_id>/update/', views.schedule_update, name='schedule_update'),
    path('schedule/<int:schedule_id>/delete/', views.schedule_delete, name='schedule_delete'),
    
    # Оценки
    path('grades/create/', views.grade_create, name='grade_create'),
    path('grades/<int:grade_id>/update/', views.grade_update, name='grade_update'),
    path('grades/<int:grade_id>/delete/', views.grade_delete, name='grade_delete'),
    

    # Предметы
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:subject_id>/update/', views.subject_update, name='subject_update'),
    path('subjects/<int:subject_id>/delete/', views.subject_delete, name='subject_delete'),
    
    # Аудитории
    path('classrooms/create/', views.classroom_create, name='classroom_create'),
    path('classrooms/<int:classroom_id>/update/', views.classroom_update, name='classroom_update'),
    path('classrooms/<int:classroom_id>/delete/', views.classroom_delete, name='classroom_delete'),
    

]


