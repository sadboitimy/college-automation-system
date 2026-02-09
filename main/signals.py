from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

@receiver(post_migrate)
def create_user_groups_and_permissions(sender, **kwargs):
    """Создает группы пользователей и настраивает права при миграциях"""
    
    # Создаем группы если их нет
    groups_data = [
        {
            'name': 'Студент',
            'description': 'Студент - может просматривать свои данные, расписание, оценки'
        },
        {
            'name': 'Преподаватель', 
            'description': 'Преподаватель - может ставить оценки, просматривать студентов и расписание'
        },
        {
            'name': 'Администратор',
            'description': 'Администратор - полный доступ ко всем функциям'
        }
    ]
    
    for group_info in groups_data:
        group, created = Group.objects.get_or_create(name=group_info['name'])
        if created:
            print(f"✓ Создана группа: {group_info['name']}")
            if 'description' in group_info:
                # Сохраняем описание в дополнительном поле если нужно
                pass
    
    print("✓ Группы пользователей инициализированы")