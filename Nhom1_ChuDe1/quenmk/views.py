import random
import time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail

def send_otp_email(email, otp):
    print(f"--- MOCK EMAIL: Mã OTP của {email} là {otp} ---")
    try:
        subject = 'Mã xác thực lấy lại mật khẩu'
        message = f'Mã xác nhận quên mật khẩu của bạn là: {otp}. Mã có hiệu lực trong 60 giây.'
        email_from = getattr(settings, 'EMAIL_HOST_USER', 'noreply@example.com')
        send_mail(subject, message, email_from, [email])
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

def nhap_sdt(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Email không được để trống.')
            return render(request, 'quenmk/nhap_sdt.html')
        
        # Check if user exists
        if not User.objects.filter(email=email).exists():
            messages.error(request, 'Email chưa được đăng ký.')
            return render(request, 'quenmk/nhap_sdt.html')
        
        otp = str(random.randint(10000, 99999)) # 5 digits
        
        # Save to session
        request.session['reset_otp_data'] = {
            'email': email,
            'otp': otp,
            'timestamp': time.time()
        }
        
        send_otp_email(email, otp)
        
        # Hiển thị mã OTP lên màn hình để test
        messages.success(request, f"Mã OTP xác thực để cấp lại mật khẩu đã được gửi về email {email}, có hiệu lực trong 1 phút.")
        
        return redirect('nhap_otp')
        
    return render(request, 'quenmk/nhap_sdt.html')

def nhap_otp(request):
    if 'reset_otp_data' not in request.session:
        return redirect('nhap_sdt')
        
    otp_data = request.session['reset_otp_data']
    email = otp_data['email']
    
    if request.method == 'POST':
        # Check if resend requested
        if 'resend' in request.POST:
            otp = str(random.randint(10000, 99999))
            request.session['reset_otp_data'] = {
                'email': email,
                'otp': otp,
                'timestamp': time.time()
            }
            send_otp_email(email, otp)
            messages.success(request, f"Mã OTP xác thực để cấp lại mật khẩu đã được gửi về email {email}, có hiệu lực trong 1 phút.")
            return redirect('nhap_otp')

        entered_otp = "".join([
            request.POST.get('otp1', ''),
            request.POST.get('otp2', ''),
            request.POST.get('otp3', ''),
            request.POST.get('otp4', ''),
            request.POST.get('otp5', '')
        ])
        
        elapsed_time = time.time() - otp_data['timestamp']
        
        if elapsed_time > 60:
            messages.error(request, 'Mã OTP đã hết hiệu lực. Vui lòng gửi lại.')
            return render(request, 'quenmk/nhap_otp.html', {'email': email})
            
        if entered_otp == otp_data['otp']:
            request.session['otp_verified'] = email
            del request.session['reset_otp_data']
            return redirect('tao_mk_moi')
        else:
            messages.error(request, 'Mã OTP không đúng.')
            
    return render(request, 'quenmk/nhap_otp.html', {'email': email})

def tao_mk_moi(request):
    if 'otp_verified' not in request.session:
        return redirect('nhap_sdt')
        
    email = request.session['otp_verified']
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if not password or not confirm_password:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin.')
            return render(request, 'quenmk/tao_mk_moi.html')
            
        if len(password) < 6:
            messages.error(request, 'Mật khẩu phải có ít nhất 6 ký tự.')
            return render(request, 'quenmk/tao_mk_moi.html')
            
        if password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp.')
            return render(request, 'quenmk/tao_mk_moi.html')
            
        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            del request.session['otp_verified']
            return redirect('thanh_cong')
        except User.DoesNotExist:
            messages.error(request, 'Tài khoản không tồn tại.')
            return redirect('nhap_sdt')
            
    return render(request, 'quenmk/tao_mk_moi.html')

def thanh_cong(request):
    return render(request, 'quenmk/thanh_cong.html')
