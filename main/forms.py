from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import (Subjects, Teachers, Attendance, Students, Classrooms, Grades, Groups, Schedule)

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавление Bootstrap классов всем полям
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control'
            })


class CustomAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавление Bootstrap классов
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })

# Форма для групп
class GroupsForm(forms.ModelForm):
    class Meta:
        model = Groups
        fields = ['GroupName', 'Course', 'Specialization']
        widgets = {
            'GroupName': forms.TextInput(attrs={'class': 'form-control'}),
            'Course': forms.Select(attrs={'class': 'form-control'}),
            'Specialization': forms.Select(attrs={'class': 'form-control'}),
        }

# Форма для студентов
class StudentsForm(forms.ModelForm):
    class Meta:
        model = Students
        fields = ['Name', 'Group', 'DateOfBirth', 'TokenNum', 'Email']
        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Group': forms.Select(attrs={'class': 'form-control'}),
            'DateOfBirth': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'TokenNum': forms.TextInput(attrs={'class': 'form-control'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

# Форма для учителей
class TeachersForm(forms.ModelForm):
    class Meta:
        model = Teachers
        fields = ['Name', 'Post', 'Department', 'Email']
        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Post': forms.TextInput(attrs={'class': 'form-control'}),
            'Department': forms.TextInput(attrs={'class': 'form-control'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

# Форма для предметов
class SubjectsForm(forms.ModelForm):
    class Meta:
        model = Subjects
        fields = ['SubjectName', 'Description', 'NumOfHours', 'Teacher']
        widgets = {
            'SubjectName': forms.TextInput(attrs={'class': 'form-control'}),
            'Description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'NumOfHours': forms.NumberInput(attrs={'class': 'form-control'}),
            'Teacher': forms.Select(attrs={'class': 'form-control'}),
        }

# Форма для кабинетов
class ClassroomsForm(forms.ModelForm):
    class Meta:
        model = Classrooms
        fields = ['Number', 'Building', 'Capacity']
        widgets = {
            'Number': forms.NumberInput(attrs={'class': 'form-control'}),
            'Building': forms.TextInput(attrs={'class': 'form-control'}),
            'Capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Форма для расписания
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['Date', 'Time', 'Subject', 'Classroom', 'Teacher', 'Group']
        widgets = {
            'Date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'Time': forms.TimeInput(
                attrs={'class': 'form-control', 'type': 'time'}
            ),
            'Subject': forms.Select(attrs={'class': 'form-control'}),
            'Classroom': forms.Select(attrs={'class': 'form-control'}),
            'Teacher': forms.Select(attrs={'class': 'form-control'}),
            'Group': forms.Select(attrs={'class': 'form-control'}),
        }

# Форма для оценок
class GradesForm(forms.ModelForm):
    class Meta:
        model = Grades
        fields = ['Student', 'Subject', 'Date', 'GradeType', 'Mark']
        widgets = {
            'Student': forms.Select(attrs={'class': 'form-control'}),
            'Subject': forms.Select(attrs={'class': 'form-control'}),
            'Date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'GradeType': forms.Select(attrs={'class': 'form-control'}),
            'Mark': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0, 'max': 100}
            ),
        }