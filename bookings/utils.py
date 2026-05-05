from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def _base_url():
    return getattr(settings, 'BASE_URL', 'http://localhost:8000')


def send_booking_notification_to_admin(booking):
    """แจ้ง Admin ทุกคนเมื่อมีการจองใหม่"""
    admin_emails = list(
        User.objects.filter(role='ADMIN').exclude(email='').values_list('email', flat=True)
    )
    if not admin_emails:
        # fallback ส่งให้ EMAIL_HOST_USER ถ้าไม่มี Admin ที่มี email
        fallback = getattr(settings, 'EMAIL_HOST_USER', '')
        if fallback and fallback != 'YOUR_EMAIL@gmail.com':
            admin_emails = [fallback]
        else:
            return

    purpose = booking.course_name if booking.purpose_type == 'TEACHING' else booking.topic
    subject = f'[แจ้งเตือน] มีรายการจองใหม่: ห้อง {booking.room.code}'
    message = (
        f'มีรายการจองใหม่รอการอนุมัติ\n\n'
        f'ผู้จอง: {booking.requester.get_full_name() or booking.requester.username}\n'
        f'อีเมล: {booking.requester.email}\n'
        f'ห้อง: {booking.room.code} — {booking.room.name}\n'
        f'วัตถุประสงค์: {purpose or "-"}\n'
        f'วันที่: {booking.start_date} ถึง {booking.end_date}\n'
        f'เวลา: {booking.start_time.strftime("%H:%M")} - {booking.end_time.strftime("%H:%M")}\n\n'
        f'อนุมัติได้ที่: {_base_url()}/admin-panel/'
    )

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, admin_emails, fail_silently=False)
    except Exception as e:
        print(f'[Email Error] send_booking_notification_to_admin: {e}')


def send_booking_status_update(booking):
    """แจ้งผู้จองเมื่อสถานะเปลี่ยน (อนุมัติ / ปฏิเสธ / ยกเลิก)"""
    recipient = booking.requester.email or getattr(settings, 'EMAIL_HOST_USER', '')
    if not recipient:
        return

    STATUS_LABEL = {
        'APPROVED': 'อนุมัติแล้ว ✅',
        'REJECTED': 'ถูกปฏิเสธ ❌',
        'CANCELLED': 'ถูกยกเลิก',
    }
    status_text = STATUS_LABEL.get(booking.status, booking.get_status_display())
    purpose = booking.course_name if booking.purpose_type == 'TEACHING' else booking.topic

    subject = f'[แจ้งผลการจอง] ห้อง {booking.room.code} — {status_text}'
    message = (
        f'เรียน {booking.requester.get_full_name() or booking.requester.username}\n\n'
        f'สถานะการจองห้อง {booking.room.code} ของคุณได้รับการอัปเดตเป็น: {status_text}\n\n'
        f'รายละเอียด:\n'
        f'  ห้อง: {booking.room.code} — {booking.room.name}\n'
        f'  วัตถุประสงค์: {purpose or "-"}\n'
        f'  วันที่: {booking.start_date} ถึง {booking.end_date}\n'
        f'  เวลา: {booking.start_time.strftime("%H:%M")} - {booking.end_time.strftime("%H:%M")}\n'
    )

    if booking.status == 'REJECTED' and booking.rejection_reason:
        message += f'\nเหตุผลที่ปฏิเสธ: {booking.rejection_reason}\n'

    message += f'\nดูรายการจองของคุณได้ที่: {_base_url()}/bookings/my/'

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
    except Exception as e:
        print(f'[Email Error] send_booking_status_update: {e}')


def send_cancellation_notice_to_admin(booking):
    """แจ้ง Admin เมื่อผู้จองยกเลิกเอง"""
    admin_emails = list(
        User.objects.filter(role='ADMIN').exclude(email='').values_list('email', flat=True)
    )
    if not admin_emails:
        return

    purpose = booking.course_name if booking.purpose_type == 'TEACHING' else booking.topic
    subject = f'[แจ้งเตือน] ผู้จองยกเลิกการจอง: ห้อง {booking.room.code}'
    message = (
        f'ผู้จองยกเลิกการจองด้วยตนเอง\n\n'
        f'ผู้จอง: {booking.requester.get_full_name() or booking.requester.username}\n'
        f'อีเมล: {booking.requester.email}\n'
        f'ห้อง: {booking.room.code} — {booking.room.name}\n'
        f'วัตถุประสงค์: {purpose or "-"}\n'
        f'วันที่: {booking.start_date} ถึง {booking.end_date}\n'
        f'เวลา: {booking.start_time.strftime("%H:%M")} - {booking.end_time.strftime("%H:%M")}\n'
    )

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, admin_emails, fail_silently=False)
    except Exception as e:
        print(f'[Email Error] send_cancellation_notice_to_admin: {e}')
