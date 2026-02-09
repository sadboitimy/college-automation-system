def user_permissions(request):
    if request.user.is_authenticated:
        return {
            'is_admin': request.user.is_staff,
            'is_teacher': request.user.groups.filter(name='Преподаватель').exists(),
            'is_student': request.user.groups.filter(name='Студент').exists(),
            'user_role': 'admin' if request.user.is_staff else 
                        'teacher' if request.user.groups.filter(name='Преподаватель').exists() else 
                        'student' if request.user.groups.filter(name='Студент').exists() else 
                        'none'
        }
    return {}