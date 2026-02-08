from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from .models import Groups, Teachers, Students, Subjects, Attendance, Schedule, Classrooms, Grades
from datetime import date, datetime, timedelta
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import StudentsForm, TeachersForm, GroupsForm, SubjectsForm, ScheduleForm, GradesForm, ClassroomsForm
from django.utils import timezone


# Главная страница
def home(request):
    if not request.user.is_authenticated:
        return render(request, 'home.html')
    

    context = {
        'students_count': Students.objects.count(),
        'teachers_count': Teachers.objects.count(),
        'groups_count': Groups.objects.count(),
        'subjects_count': Subjects.objects.count(),
        'schedule_count': Schedule.objects.count(),
    }
    
    return render(request, 'home.html', context)

# Вход
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Неправильный логин или пароль')
    
    return render(request, 'login.html')

# Регистрация
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return render(request, 'register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        
        login(request, user)
        messages.success(request, 'Регистрация успешна!')
        return redirect('home')
    
    return render(request, 'register.html')

# Выход
@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')

# Страница со списком студентов
@login_required
def students_list(request):
    students = Students.objects.all().order_by('Name')
    
    group_id = request.GET.get('group', '')
    if group_id:
        students = students.filter(Group_id=group_id)
    
    search = request.GET.get('search', '')
    if search:
        students = students.filter(Name__icontains=search)
    
    groups = Groups.objects.all()
    
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'students': page_obj,
        'groups': groups,
        'selected_group': group_id,
        'search_query': search,
    }
    return render(request, 'students/list.html', context)

# Cтраница студента
@login_required
def student_detail(request, student_id):
    student = Students.objects.get(id=student_id)
    
    grades = Grades.objects.filter(Student=student).order_by('-Date')
    
    attendance = Attendance.objects.filter(Student=student).order_by('-Date')
    
    schedule = Schedule.objects.filter(Group=student.Group).order_by('Date', 'Time')
    
    context = {
        'student': student,
        'grades': grades,
        'attendance': attendance,
        'schedule': schedule[:10],
    }
    return render(request, 'students/detail.html', context)

# Страница со списком преподавателей
@login_required
def teachers_list(request):
    teachers = Teachers.objects.all().order_by('Name')
    
    search = request.GET.get('search', '')
    if search:
        teachers = teachers.filter(Name__icontains=search)
    
    department = request.GET.get('department', '')
    if department:
        teachers = teachers.filter(Department__icontains=department)
    
    departments = Teachers.objects.values_list('Department', flat=True).distinct()
    
    context = {
        'teachers': teachers,
        'departments': departments,
        'search_query': search,
        'selected_department': department,
    }
    return render(request, 'teachers/list.html', context)

# Cтраница преподавателя
@login_required
def teacher_detail(request, teacher_id):
    teacher = Teachers.objects.get(id=teacher_id)
    
    subjects = Subjects.objects.filter(Teacher=teacher)
    
    schedule = Schedule.objects.filter(Teacher=teacher).order_by('Date', 'Time')
    
    context = {
        'teacher': teacher,
        'subjects': subjects,
        'schedule': schedule[:10],
    }
    return render(request, 'teachers/detail.html', context)

# Страница расписания
@login_required
def schedule_view(request):
    group_id = request.GET.get('group', '')
    teacher_id = request.GET.get('teacher', '')
    date_filter = request.GET.get('date', '')
    
    selected_group_obj = None
    if group_id:
        try:
            selected_group_obj = Groups.objects.get(id=group_id)
        except Groups.DoesNotExist:
            selected_group_obj = None
    
    if not date_filter:
        selected_date = datetime.now().date()
        date_filter_str = selected_date.strftime('%Y-%m-%d')
    else:
        try:
            selected_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            date_filter_str = date_filter
        except ValueError:
            selected_date = datetime.now().date()
            date_filter_str = selected_date.strftime('%Y-%m-%d')
    
    week_schedule = []
    schedule_for_date = []
    grouped_schedule = {}
    
    if group_id and selected_group_obj:
        start_of_week = selected_date - timedelta(days=selected_date.weekday())
        
        for i in range(6):
            day_date = start_of_week + timedelta(days=i)
            day_lessons = Schedule.objects.filter(
                Group_id=group_id,
                Date=day_date
            ).order_by('Time')
            
            if teacher_id:
                day_lessons = day_lessons.filter(Teacher_id=teacher_id)
            
            week_schedule.append({
                'date': day_date,
                'day_name': ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'][i],
                'lessons': day_lessons
            })
        
        schedule_for_date = Schedule.objects.none()
    
    else:
        schedule_for_date = Schedule.objects.filter(Date=selected_date).order_by('Time')
        
        if teacher_id:
            schedule_for_date = schedule_for_date.filter(Teacher_id=teacher_id)
        
        for lesson in schedule_for_date:
            group_id_key = lesson.Group.id
            if group_id_key not in grouped_schedule:
                grouped_schedule[group_id_key] = {
                    'group': lesson.Group,
                    'lessons': []
                }
            grouped_schedule[group_id_key]['lessons'].append(lesson)
    
    groups = Groups.objects.all()
    teachers = Teachers.objects.all()
    
    context = {
        'schedule': schedule_for_date,
        'grouped_schedule': grouped_schedule,
        'groups': groups,
        'teachers': teachers,
        'selected_group': group_id,
        'selected_group_obj': selected_group_obj,
        'selected_teacher': teacher_id,
        'selected_date': selected_date,
        'date_filter': date_filter_str,
        'week_schedule': week_schedule,
    }
    return render(request, 'schedule/list.html', context)


# Конкретное занятие в расписании
@login_required
def schedule_detail(request, schedule_id):
    schedule_item = get_object_or_404(Schedule, id=schedule_id)
    
    students = Students.objects.filter(Group=schedule_item.Group)
    
    similar_schedule = Schedule.objects.filter(
        Date=schedule_item.Date,
        Time=schedule_item.Time
    ).exclude(id=schedule_item.id)[:3]
    
    
    context = {
        'schedule': schedule_item,
        'students': students,
        'similar_schedule': similar_schedule,
    }
    return render(request, 'schedule/detail.html', context)

# Страница с оценками
@login_required
def grades_view(request):
    grades = Grades.objects.all().order_by('-Date')
    
    student_id = request.GET.get('student', '')
    subject_id = request.GET.get('subject', '')
    grade_type = request.GET.get('type', '')
    
    if student_id:
        grades = grades.filter(Student_id=student_id)
    
    if subject_id:
        grades = grades.filter(Subject_id=subject_id)
    
    if grade_type:
        grades = grades.filter(GradeType=grade_type)
    
    students = Students.objects.all()
    subjects = Subjects.objects.all()
    grade_types = [choice[0] for choice in Grades.GradeType_list]
    
    context = {
        'grades': grades,
        'students': students,
        'subjects': subjects,
        'grade_types': grade_types,
        'selected_student': student_id,
        'selected_subject': subject_id,
        'selected_type': grade_type,
    }
    return render(request, 'grades/list.html', context)

# Страница с оценкой
@login_required
def grade_detail(request, grade_id):
    grade = get_object_or_404(Grades, id=grade_id)
    
    other_grades = Grades.objects.filter(
        Student=grade.Student,
        Subject=grade.Subject
    ).exclude(id=grade.id).order_by('-Date')[:5]
    
    context = {
        'grade': grade,
        'other_grades': other_grades,
    }
    return render(request, 'grades/detail.html', context)

# Страница с группами
@login_required
def groups_list(request):
    groups = Groups.objects.all().order_by('GroupName')
    
    course = request.GET.get('course', '')
    specialization = request.GET.get('specialization', '')
    
    if course:
        groups = groups.filter(Course=course)
    
    if specialization:
        groups = groups.filter(Specialization=specialization)
    
    context = {
        'groups': groups,
        'courses': range(1, 6),
        'specializations': Groups.Specs_list,
        'selected_course': course,
        'selected_specialization': specialization,
    }
    return render(request, 'groups/list.html', context)

# Cтраница группы
@login_required
def group_detail(request, group_id):
    group = Groups.objects.get(id=group_id)
    
    students = Students.objects.filter(Group=group).order_by('Name')
    
    schedule = Schedule.objects.filter(Group=group).order_by('Date', 'Time')
    
    context = {
        'group': group,
        'students': students,
        'schedule': schedule,
    }
    return render(request, 'groups/detail.html', context)

# Страница с предметами
@login_required
def subjects_list(request):
    subjects = Subjects.objects.all().order_by('SubjectName')
    
    search = request.GET.get('search', '')
    if search:
        subjects = subjects.filter(SubjectName__icontains=search)
    
    teacher_id = request.GET.get('teacher', '')
    if teacher_id:
        subjects = subjects.filter(Teacher_id=teacher_id)
    
    teachers = Teachers.objects.all()
    
    context = {
        'subjects': subjects,
        'teachers': teachers,
        'search_query': search,
        'selected_teacher': teacher_id,
    }
    return render(request, 'subjects/list.html', context)

# Страница предмета
@login_required
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    
    groups = Groups.objects.filter(schedule__Subject=subject).distinct()
    
    schedule = Schedule.objects.filter(Subject=subject).order_by('Date', 'Time')
    
    grades = Grades.objects.filter(Subject=subject).order_by('-Date')[:10]
    
    context = {
        'subject': subject,
        'groups': groups,
        'schedule': schedule,
        'grades': grades,
    }
    return render(request, 'subjects/detail.html', context)

# Страница с аудиториями
@login_required
def classrooms_list(request):
    classrooms = Classrooms.objects.all().order_by('Building', 'Number')
    
    building = request.GET.get('building', '')
    if building:
        classrooms = classrooms.filter(Building__icontains=building)
    
    min_capacity = request.GET.get('min_capacity', '')
    if min_capacity:
        classrooms = classrooms.filter(Capacity__gte=min_capacity)
    
    buildings = Classrooms.objects.values_list('Building', flat=True).distinct()
    
    context = {
        'classrooms': classrooms,
        'buildings': buildings,
        'selected_building': building,
        'selected_min_capacity': min_capacity,
    }
    return render(request, 'classrooms/list.html', context)

# Страница аудитория
@login_required
def classroom_detail(request, classroom_id):
    classroom = get_object_or_404(Classrooms, id=classroom_id)
    
    schedule = Schedule.objects.filter(Classroom=classroom).order_by('Date', 'Time')
    
    context = {
        'classroom': classroom,
        'schedule': schedule,
    }
    return render(request, 'classrooms/detail.html', context)

# Страница с посещаемостью
@login_required
def schedule_attendance(request, schedule_id):
    schedule_item = get_object_or_404(Schedule, id=schedule_id)
    
    students = Students.objects.filter(Group=schedule_item.Group).order_by('Name')
    
    if request.method == 'POST':
        for student in students:
            status_key = f'status_{student.id}'
            reason_key = f'reason_{student.id}'
            
            status = request.POST.get(status_key, 'attended')
            reason = request.POST.get(reason_key, '')
            
            attendance, created = Attendance.objects.update_or_create(
                Student=student,
                Subject=schedule_item.Subject,
                Date=schedule_item.Date,
                Schedule=schedule_item,
                defaults={
                    'Status': status,
                    'Reason': reason if status in ['absent', 'valid_reason'] else ''
                }
            )
        
        messages.success(request, 'Посещаемость успешно сохранена!')
        
        return redirect('schedule_detail', schedule_id=schedule_id)
    
    attendance_records = {}
    for student in students:
        attendance = Attendance.objects.filter(
            Student=student,
            Schedule=schedule_item,
            Date=schedule_item.Date
        ).first()
        attendance_records[student.id] = attendance
    
    context = {
        'schedule': schedule_item,
        'students': students,
        'attendance_records': attendance_records,
    }
    
    return render(request, 'schedule/attendance.html', context)


# ========== Студенты CRUD ==========

@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Студент успешно добавлен!')
            return redirect('students_list')
    else:
        form = StudentsForm()
    
    return render(request, 'students/form.html', {
        'form': form,
        'title': 'Добавить студента',
        'action': 'create'
    })

@login_required
def student_update(request, student_id):
    student = get_object_or_404(Students, id=student_id)
    
    if request.method == 'POST':
        form = StudentsForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные студента обновлены!')
            return redirect('student_detail', student_id=student.id)
    else:
        form = StudentsForm(instance=student)
    
    return render(request, 'students/form.html', {
        'form': form,
        'title': 'Редактировать студента',
        'action': 'update',
        'student': student
    })

@login_required
def student_delete(request, student_id):
    student = get_object_or_404(Students, id=student_id)
    
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Студент удален!')
        return redirect('students_list')
    
    return render(request, 'students/confirm_delete.html', {
        'student': student
    })

# ========== Преподаватели CRUD ==========

@login_required
def teacher_create(request):
    if request.method == 'POST':
        form = TeachersForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Преподаватель успешно добавлен!')
            return redirect('teachers_list')
    else:
        form = TeachersForm()
    
    return render(request, 'teachers/form.html', {
        'form': form,
        'title': 'Добавить преподавателя',
        'action': 'create'
    })

@login_required
def teacher_update(request, teacher_id):
    teacher = get_object_or_404(Teachers, id=teacher_id)
    
    if request.method == 'POST':
        form = TeachersForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные преподавателя обновлены!')
            return redirect('teacher_detail', teacher_id=teacher.id)
    else:
        form = TeachersForm(instance=teacher)
    
    return render(request, 'teachers/form.html', {
        'form': form,
        'title': 'Редактировать преподавателя',
        'action': 'update',
        'teacher': teacher
    })

@login_required
def teacher_delete(request, teacher_id):
    teacher = get_object_or_404(Teachers, id=teacher_id)
    
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, 'Преподаватель удален!')
        return redirect('teachers_list')
    
    return render(request, 'teachers/confirm_delete.html', {
        'teacher': teacher
    })

# ========== Группы CRUD ==========

@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Группа успешно добавлена!')
            return redirect('groups_list')
    else:
        form = GroupsForm()
    
    return render(request, 'groups/form.html', {
        'form': form,
        'title': 'Добавить группу',
        'action': 'create'
    })

@login_required
def group_update(request, group_id):
    group = get_object_or_404(Groups, id=group_id)
    
    if request.method == 'POST':
        form = GroupsForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные группы обновлены!')
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupsForm(instance=group)
    
    return render(request, 'groups/form.html', {
        'form': form,
        'title': 'Редактировать группу',
        'action': 'update',
        'group': group
    })

@login_required
def group_delete(request, group_id):
    group = get_object_or_404(Groups, id=group_id)
    
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Группа удалена!')
        return redirect('groups_list')
    
    return render(request, 'groups/confirm_delete.html', {
        'group': group
    })

# ========== Расписание CRUD ==========

@login_required
def schedule_create(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Занятие добавлено в расписание!')
            return redirect('schedule')
    else:
        form = ScheduleForm()
    
    return render(request, 'schedule/form.html', {
        'form': form,
        'title': 'Добавить занятие',
        'action': 'create'
    })

@login_required
def schedule_update(request, schedule_id):
    schedule_item = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Занятие обновлено!')
            return redirect('schedule')
    else:
        form = ScheduleForm(instance=schedule_item)
    
    return render(request, 'schedule/form.html', {
        'form': form,
        'title': 'Редактировать занятие',
        'action': 'update',
        'schedule_item': schedule_item
    })

@login_required
def schedule_delete(request, schedule_id):
    schedule_item = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        schedule_item.delete()
        messages.success(request, 'Занятие удалено из расписания!')
        return redirect('schedule')
    
    return render(request, 'schedule/confirm_delete.html', {
        'schedule_item': schedule_item
    })

# ========== Оценки CRUD ==========

@login_required
def grade_create(request):
    if request.method == 'POST':
        form = GradesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Оценка добавлена!')
            return redirect('grades_list')
    else:
        form = GradesForm()
    
    return render(request, 'grades/form.html', {
        'form': form,
        'title': 'Добавить оценку',
        'action': 'create'
    })

@login_required
def grade_update(request, grade_id):
    grade = get_object_or_404(Grades, id=grade_id)
    
    if request.method == 'POST':
        form = GradesForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Оценка обновлена!')
            return redirect('grades_list')
    else:
        form = GradesForm(instance=grade)
    
    return render(request, 'grades/form.html', {
        'form': form,
        'title': 'Редактировать оценку',
        'action': 'update',
        'grade': grade
    })

@login_required
def grade_delete(request, grade_id):
    grade = get_object_or_404(Grades, id=grade_id)
    
    if request.method == 'POST':
        grade.delete()
        messages.success(request, 'Оценка удалена!')
        return redirect('grades_list')
    
    return render(request, 'grades/confirm_delete.html', {
        'grade': grade
    })

# ========== Предметы CRUD ==========

@login_required
def subject_create(request):
    if request.method == 'POST':
        form = SubjectsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Предмет успешно добавлен!')
            return redirect('subjects_list')
    else:
        form = SubjectsForm()
    
    return render(request, 'subjects/form.html', {
        'form': form,
        'title': 'Добавить предмет',
        'action': 'create'
    })

@login_required
def subject_update(request, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    
    if request.method == 'POST':
        form = SubjectsForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные предмета обновлены!')
            return redirect('subject_detail', subject_id=subject.id)
    else:
        form = SubjectsForm(instance=subject)
    
    return render(request, 'subjects/form.html', {
        'form': form,
        'title': 'Редактировать предмет',
        'action': 'update',
        'subject': subject
    })

@login_required
def subject_delete(request, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Предмет удален!')
        return redirect('subjects_list')
    
    return render(request, 'subjects/confirm_delete.html', {
        'subject': subject
    })

# ========== Аудитории CRUD ==========

@login_required
def classroom_create(request):
    if request.method == 'POST':
        form = ClassroomsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аудитория успешно добавлена!')
            return redirect('classrooms_list')
    else:
        form = ClassroomsForm()
    
    return render(request, 'classrooms/form.html', {
        'form': form,
        'title': 'Добавить аудиторию',
        'action': 'create'
    })

@login_required
def classroom_update(request, classroom_id):
    classroom = get_object_or_404(Classrooms, id=classroom_id)
    
    if request.method == 'POST':
        form = ClassroomsForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные аудитории обновлены!')
            return redirect('classroom_detail', classroom_id=classroom.id)
    else:
        form = ClassroomsForm(instance=classroom)
    
    return render(request, 'classrooms/form.html', {
        'form': form,
        'title': 'Редактировать аудиторию',
        'action': 'update',
        'classroom': classroom
    })

@login_required
def classroom_delete(request, classroom_id):
    classroom = get_object_or_404(Classrooms, id=classroom_id)
    
    if request.method == 'POST':
        classroom.delete()
        messages.success(request, 'Аудитория удалена!')
        return redirect('classrooms_list')
    
    return render(request, 'classrooms/confirm_delete.html', {
        'classroom': classroom
    })