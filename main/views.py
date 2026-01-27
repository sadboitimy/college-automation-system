from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home_page(request):
    return HttpResponse("<h1>Добро пожаловать в систему автоматизации колледжа!</h1><p>Это главная страница.</p>")