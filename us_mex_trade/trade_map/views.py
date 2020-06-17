from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse('<h1>This is where the map will be</h1>')
    
def about(request):
    return HttpResponse('<h2> About the map</h2>')
