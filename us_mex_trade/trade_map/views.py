from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'trade_map/home.html')
    
def about(request):
    return HttpResponse('<h2> About the map</h2>')
