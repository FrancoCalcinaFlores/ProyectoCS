from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def inicio(request):
    return render(request, 'inicio.html')

@login_required
def home(request):
    if request.user.groups.filter(name='ADMIN').exists():
        return redirect('dashboard')
    elif request.user.groups.filter(name='PACIENTE').exists():
        return redirect('dashboard')
    return redirect('login')
