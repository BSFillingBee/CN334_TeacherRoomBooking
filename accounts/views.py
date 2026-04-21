from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"เข้าสู่ระบบสำเร็จ ยินดีต้อนรับคุณ {user.username}")
            return redirect('dashboard')
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง หรือคุณไม่มีสิทธิ์เข้าใช้งานระบบ")
            
    return render(request, 'registration/login.html', {'mock_enabled': settings.MOCK_API})
