from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Groups(models.Model):
# Группы

    CourseChoices=[
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
    ]

    Specs_list=[
        ('it_web', 'Веб-разработка'),
        ('auto_industrial', 'Промышленная автоматизация'),
        ('auto_robotics', 'Робототехника'),
        ('economy_banking', 'Банковское дело'),
        ('design_graphic', 'Графический дизайн'),
        ('design_interior', 'Дизайн интерьера'),
    ]
    GroupName=models.CharField(max_length=100)
    Course=models.IntegerField(choices=CourseChoices)
    Specialization=models.CharField(choices=Specs_list, max_length=100)

    def __str__(self):
        return f'GroupName={self.GroupName}, Course={self.Course}, Specialization={self.Specialization}'   
    
class Students(models.Model):
#Студенты

    Name=models.CharField(max_length=100)
    Group=models.ForeignKey(Groups, on_delete=models.SET_NULL, null=True, blank=True)
    DateOfBirth=models.DateField()
    TokenNum=models.CharField(max_length=30, unique=True)
    Email=models.EmailField()
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True,blank=True, related_name='student_profile')

    def __str__(self):
        return f'Name={self.Name}, Group={self.Group.GroupName if self.Group else "Без группы"}, DateOfBirth={self.DateOfBirth}, TokenNum={self.TokenNum}, Email={self.Email}'
    
class Teachers(models.Model):
#Преподаватели

    Name=models.CharField(max_length=100)
    Post=models.CharField(max_length=100)
    Department=models.CharField(max_length=200)
    Email=models.EmailField()
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher_profile', verbose_name='Пользователь')

    def __str__(self):
        return f'Name={self.Name}, Post={self.Post}, Department={self.Department}, Email={self.Email}'
    
class Subjects(models.Model):
#Предметы

    SubjectName=models.CharField(max_length=200)
    Description=models.TextField(blank=True)
    NumOfHours=models.PositiveIntegerField()
    Teacher=models.ForeignKey(Teachers, on_delete=models.SET_NULL, null=True, blank=True)

    def  __str__(self):
        return f'SubjectName={self.SubjectName}, Description={self.Description}, NumOfHours={self.NumOfHours}, Teacher={self.Teacher}'
    
class Classrooms(models.Model):
#Аудитории

    Number=models.IntegerField()
    Building=models.CharField(max_length=100)
    Capacity=models.PositiveIntegerField()

    def __str__(self):
        return f'Number={self.Number}, Building={self.Building}, Capacity={self.Capacity}'
    
class Schedule(models.Model):
#Расписание

    Date=models.DateField()
    Time=models.TimeField()
    Subject=models.ForeignKey(Subjects, on_delete=models.CASCADE)
    Classroom=models.ForeignKey(Classrooms, on_delete=models.SET_NULL, null=True, blank=True)
    Teacher=models.ForeignKey(Teachers, on_delete=models.SET_NULL, null=True, blank=True)
    Group=models.ForeignKey(Groups, on_delete=models.CASCADE)

    def __str__(self):
        return f'Date={self.Date}, Time={self.Time}, Subject={self.Subject}, Classroom={self.Classroom}, Teacher={self.Teacher}, Group={self.Group}'
    
class Grades(models.Model):
#Оценки

    GradeType_list=[
        ('test', 'Зачет'),
        ('exam', 'Экзамен'),
        ('currrent_control', 'Текущий контроль'),
    ]
    Student=models.ForeignKey(Students, on_delete=models.CASCADE)
    Subject=models.ForeignKey(Subjects, on_delete=models.CASCADE)
    Date=models.DateField()
    GradeType=models.CharField(choices=GradeType_list, max_length=30)
    Mark=models.PositiveIntegerField(
        validators=[MinValueValidator(0, message='Значение не может быть меньше 0'),
                    MaxValueValidator(100, message='Значение не может быть больше 100')],
                    default=0)
    
class Attendance(models.Model):
#Посещаемость

    Status_list=[
        ('attended', 'Присутствовал'),
        ('absent', 'Отсутствовал'),
        ('valid_reason', 'Уважительная причина',)
    ]

    Student=models.ForeignKey(Students, on_delete=models.CASCADE)
    Subject=models.ForeignKey(Subjects, on_delete=models.CASCADE)
    Status=models.CharField(choices=Status_list, max_length=30)
    Schedule=models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True, blank=True)
    Date=models.DateField()
    Reason=models.TextField(blank=True, null=True)
    Created_at=models.DateTimeField(default=timezone.now)
    Updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Student={self.Student}, subject={self.Subject}, Date={self.Date}, Status={self.Status}'