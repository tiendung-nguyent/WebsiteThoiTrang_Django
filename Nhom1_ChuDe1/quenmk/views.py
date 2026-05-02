import random
import time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
try:
    from twilio.rest import Client
except ImportError:
    Client = None

def send_otp_sms(phone, otp):
    print(f"--- MOCK SMS: Mã OTP của số {phone} là {otp} ---")
    if Client and getattr(settings, 'TWILIO_ACCOUNT_SID', None) and settings.TWILIO_ACCOUNT_SID != 'YOUR_TWILIO_ACCOUNT_SID':
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # Twilio needs +84 format for Vietnam. Assuming phone is like 09xxxx
            if phone.startswith('0'):
                formatted_phone = '+84' + phone[1:]
            else:
                formatted_phone = phone
            
            message = client.messages.create(
                body=f"Mã xác nhận quên mật khẩu của bạn là: {otp}. Mã có hiệu lực trong 60 giây.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=formatted_phone
            )
            print(f"SMS sent successfully: {message.sid}")
        except Exception as e:
            print(f"Error sending SMS via Twilio: {e}")

def nhap_sdt(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        if not phone:
            messages.error(request, 'Số điện thoại không được để trống.')
            return render(request, 'quenmk/nhap_sdt.html')
        
        # Check if user exists. System uses username as phone in accounts
        if not User.objects.filter(username=phone).exists():
            messages.error(request, 'Số điện thoại chưa được đăng ký.')
            return render(request, 'quenmk/nhap_sdt.html')
        
        otp = str(random.randint(10000, 99999)) # 5 digits as per screenshot
        
        # Save to session
        request.session['reset_otp_data'] = {
            'phone': phone,
            'otp': otp,
            'timestamp': time.time()
        }
        
        send_otp_sms(phone, otp)
        
        # Hiển thị mã OTP lên màn hình để test
        messages.success(request, f"Mã OTP xác thực để cấp lại mật khẩu của bạn là {otp}, có hiệu lực trong 1 phút.")
        
        return redirect('nhap_otp')
        
    return render(request, 'quenmk/nhap_sdt.html')

def nhap_otp(request):
    if 'reset_otp_data' not in request.session:
        return redirect('nhap_sdt')
        
    otp_data = request.session['reset_otp_data']
    phone = otp_data['phone']
    
    if request.method == 'POST':
        # Check if resend requested
        if 'resend' in request.POST:
            otp = str(random.randint(10000, 99999))
            request.session['reset_otp_data'] = {
                'phone': phone,
                'otp': otp,
                'timestamp': time.time()
            }
            send_otp_sms(phone, otp)
            messages.success(request, f"Mã OTP xác thực để cấp lại mật khẩu của bạn là {otp}, có hiệu lực trong 1 phút.")
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
            return render(request, 'quenmk/nhap_otp.html', {'phone': phone})
            
        if entered_otp == otp_data['otp']:
            request.session['otp_verified'] = phone
            del request.session['reset_otp_data']
            return redirect('tao_mk_moi')
        else:
            messages.error(request, 'Mã OTP không đúng.')
            
    return render(request, 'quenmk/nhap_otp.html', {'phone': phone})

def tao_mk_moi(request):
    if 'otp_verified' not in request.session:
        return redirect('nhap_sdt')
        
    phone = request.session['otp_verified']
    
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
            user = User.objects.get(username=phone)
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
