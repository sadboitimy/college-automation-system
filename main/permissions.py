from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Преподаватель').exists()

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Студент').exists()

class StudentProfileAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_authenticated
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if request.user.groups.filter(name='Преподаватель').exists():
            return view.action in ['retrieve', 'list']
        if request.user.groups.filter(name='Студент').exists():
            try:
                student_profile = request.user.student_profile
                return obj.id == student_profile.id and view.action in ['retrieve']
            except:
                return False
        return False

class TeacherProfileAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return request.user.is_authenticated
        return request.user.is_staff

class GroupAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return request.user.is_authenticated
        return request.user.is_staff

class SubjectAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return request.user.is_authenticated
        return request.user.is_staff

class ScheduleAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return request.user.is_authenticated
        return request.user.is_staff

class ClassroomAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return request.user.is_authenticated
        return request.user.is_staff

class GradeAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list']:
            return request.user.is_authenticated
        if view.action in ['create', 'update', 'partial_update', 'destroy']:
            return request.user.is_staff or request.user.groups.filter(name='Преподаватель').exists()
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if request.user.groups.filter(name='Преподаватель').exists():
            return True
        if request.user.groups.filter(name='Студент').exists():
            try:
                student_profile = request.user.student_profile
                return obj.Student.id == student_profile.id and view.action in ['retrieve']
            except:
                return False
        return False

class StudentScheduleAccess:
    def filter_queryset(self, request, queryset):
        if request.user.groups.filter(name='Студент').exists():
            try:
                student = request.user.student_profile
                if student.Group:
                    return queryset.filter(Group=student.Group)
            except:
                pass
        return queryset

class StudentGradeAccess:
    def filter_queryset(self, request, queryset):
        if request.user.is_staff or request.user.groups.filter(name='Преподаватель').exists():
            return queryset
        if request.user.groups.filter(name='Студент').exists():
            try:
                student = request.user.student_profile
                return queryset.filter(Student=student)
            except:
                pass
        return queryset.none()

class StudentSubjectAccess:
    def filter_queryset(self, request, queryset):
        if request.user.is_staff or request.user.groups.filter(name='Преподаватель').exists():
            return queryset
        if request.user.groups.filter(name='Студент').exists():
            try:
                student = request.user.student_profile
                if student.Group:
                    return queryset.filter(schedule__Group=student.Group).distinct()
            except:
                pass
        return queryset.none()