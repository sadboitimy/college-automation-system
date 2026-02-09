from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    """Только админ"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            raise PermissionDenied("Доступ запрещен. Требуются права администратора.")
        return view_func(request, *args, **kwargs)
    return wrapper

def teacher_or_admin_required(view_func):
    """Преподаватель или админ"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        # Проверяем группы по имени
        user_groups = request.user.groups.all()
        group_names = [group.name for group in user_groups]
        
        if not (request.user.is_staff or 'Преподаватель' in group_names):
            raise PermissionDenied("Доступ запрещен. Требуются права преподавателя или администратора.")
        return view_func(request, *args, **kwargs)
    return wrapper

def student_or_teacher_or_admin_required(view_func):
    """Любой пользователь"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper