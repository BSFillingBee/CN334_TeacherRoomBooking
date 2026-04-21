from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

def send_booking_notification_to_admin(booking):
    """Notify all Admins when a new booking is created."""
    admins = User.objects.filter(role='ADMIN')
    admin_emails = [admin.email for admin in admins if admin.email]
    
    if not admin_emails:
        return
        
    subject = f'[แจ้งเตือน] มีรายการจองใหม่: {booking.room.code}'
    message = f"""
    มีรายการจองใหม่ในระบบที่รอการตัดสินใจ:
    
    ผู้จอง: {booking.requester.username}
    ห้อง: {booking.room.code} ({booking.room.name})
    วัตถุประสงค์: {booking.course_name if booking.purpose_type == 'TEACHING' else booking.topic}
    วันที่: {booking.start_date} ถึง {booking.end_date}
    เวลา: {booking.start_time} - {booking.end_time}
    
    กรุณาตรวจสอบและอนุมัติในระบบ: {settings.BASE_URL if hasattr(settings, 'BASE_URL') else 'http://localhost:8000'}/bookings/admin/approvals/
    """
    
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, admin_emails)
    except Exception as e:
        print(f"Error sending admin email: {e}")

def send_booking_status_update(booking):
    """Notify the requester when their booking status changes."""
    if not booking.requester.email:
        return
        
    status_text = booking.get_status_display()
    subject = f'[แจ้งผลการจอง] รายการจองห้อง {booking.room.code} ของคุณคือ: {status_text}'
    
    message = f"""
    เรียน คุณ {booking.requester.first_name or booking.requester.username},
    
    สถานะการจองห้อง {booking.room.code} ของคุณได้รับการอัปเดตเป็น: {status_text}
    
    รายละเอียด:
    วัตถุประสงค์: {booking.course_name if booking.purpose_type == 'TEACHING' else booking.topic}
    วันที่: {booking.start_date} ถึง {booking.end_date}
    เวลา: {booking.start_time} - {booking.end_time}
    """
    
    if booking.status == 'REJECTED':
        message += f"\nเหตุผลที่ปฏิเสธ: {booking.rejection_reason}"
        
    message += f"\n\nตรวจสอบรายละเอียดได้ที่: {settings.BASE_URL if hasattr(settings, 'BASE_URL') else 'http://localhost:8000'}/bookings/my/"
    
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [booking.requester.email])
    except Exception as e:
        print(f"Error sending user email: {e}")
