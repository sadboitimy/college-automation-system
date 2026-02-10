from django.contrib.auth.models import User, Group
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
    
    def get_role(self, obj):
        if obj.is_staff:
            return 'admin'
        elif obj.groups.filter(name='Преподаватель').exists():
            return 'teacher'
        elif obj.groups.filter(name='Студент').exists():
            return 'student'
        return 'none'

class AdminCreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователей админом"""
    password = serializers.CharField(write_only=True, required=True)
    name = serializers.CharField(write_only=True, required=True, label="ФИО")
    role = serializers.ChoiceField(
        choices=[('student', 'Студент'), ('teacher', 'Преподаватель'), ('admin', 'Администратор')],
        write_only=True,
        required=True
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'name', 'role']
    
    def create(self, validated_data):
        role = validated_data.pop('role')
        name = validated_data.pop('name')
        
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=name.split()[0] if name.split() else name,
            last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
            password=make_password(validated_data['password'])
        )
        
        if role == 'admin':
            user.is_staff = True
            user.is_superuser = True
            user.save()
        elif role == 'teacher':
            teacher_group = Group.objects.get(name='Преподаватель')
            user.groups.add(teacher_group)
        elif role == 'student':
            student_group = Group.objects.get(name='Студент')
            user.groups.add(student_group)
        
        # Создаем профиль в системе
        if role == 'teacher':
            Teachers.objects.create(
                Name=name,
                user=user
            )
        elif role == 'student':
            Students.objects.create(
                Name=name,
                user=user,
                TokenNum=f"ST{user.id:06d}"
            )
        
        return user
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

# Базовые сериализаторы
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teachers
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = '__all__'

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classrooms
        fields = '__all__'

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grades
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'