import json
import csv
from datetime import date, timedelta, datetime
from calendar import monthcalendar

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from bookings.models import Booking
from bookings.utils import send_booking_notification_to_admin, send_booking_status_update, send_cancellation_notice_to_admin
from rooms.models import Room
from django.conf import settings

User = get_user_model()

THAI_MONTHS = ['มกราคม','กุมภาพันธ์','มีนาคม','เมษายน','พฤษภาคม','มิถุนายน',
               'กรกฎาคม','สิงหาคม','กันยายน','ตุลาคม','พฤศจิกายน','ธันวาคม']
TIME_SLOTS = ['08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00']
DAYS_OF_WEEK = [
    {'value': '0', 'label': 'จันทร์'},
    {'value': '1', 'label': 'อังคาร'},
    {'value': '2', 'label': 'พุธ'},
    {'value': '3', 'label': 'พฤหัสบดี'},
    {'value': '4', 'label': 'ศุกร์'},
]
PROGRAMS = [
    {'value': 'NORMAL', 'label': 'ปริญญาตรีภาคปกติ'},
    {'value': 'MASTER', 'label': 'ปริญญาโท'},
    {'value': 'TEP_TEPE', 'label': 'TEP-TEPE'},
    {'value': 'TU_PINE', 'label': 'TU-PINE'},
]


# ─── Auth ─────────────────────────────────────────────────────────────────────

ROOM_THUMB = {
    '406-3':   'images/rooms/406-3.jpg',
    '406-5':   'images/rooms/406-5.jpg',
    '408-1':   'images/rooms/408-1.jpg',
    '408-2/1': 'images/rooms/408-2_1.jpg',
    '408-2/2': 'images/rooms/408-2_2.jpg',
}
ROOM_INROOM = {
    '406-3':   'images/rooms/inroom406-3.jpg',
    '406-5':   'images/rooms/inroom406-5.jpg',
    '408-1':   'images/rooms/408-1.jpg',
    '408-2/1': 'images/rooms/408-2_1.jpg',
    '408-2/2': 'images/rooms/408-2_2.jpg',
}

def get_room_thumb(room):
    return ROOM_THUMB.get(room.code, '')

def get_room_inroom(room):
    return ROOM_INROOM.get(room.code, '')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('admin_approval' if user.is_admin else 'dashboard')
        error = 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'
    return render(request, 'accounts/login.html', {'error': error})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')


# ─── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    if request.user.is_admin:
        return redirect('admin_approval')

    today_str = date.today().isoformat()
    today_bookings = Booking.objects.filter(
        start_date__lte=today_str, end_date__gte=today_str,
        status='APPROVED'
    ).select_related('room', 'requester')

    my_bookings = Booking.objects.filter(requester=request.user)
    pending_count = my_bookings.filter(status='PENDING').count()
    rooms_count = Room.objects.filter(is_active=True).count()

    stats = [
        {'label': 'การจองของฉัน', 'value': my_bookings.count()},
        {'label': 'รออนุมัติ', 'value': pending_count},
        {'label': 'ห้องว่างวันนี้', 'value': rooms_count - today_bookings.count()},
        {'label': 'ใช้งานเดือนนี้', 'value': my_bookings.filter(start_date__month=date.today().month).count()},
    ]

    return render(request, 'bookings/dashboard.html', {
        'today_bookings': today_bookings[:5],
        'today_bookings_count': today_bookings.count(),
        'stats': stats,
    })


# ─── Booking ────────────────────────────────────────────────────────────────────

@login_required
def book_room(request):
    rooms = Room.objects.filter(is_active=True).order_by('code')
    rooms_json = json.dumps([{'id': r.id, 'code': r.code, 'name': r.name, 'capacity': r.capacity} for r in rooms])

    selected_room_id = request.GET.get('roomId', str(rooms.first().id) if rooms.exists() else '')
    today = date.today().isoformat()
    weekday = str(date.today().weekday())
    selected_days = [weekday] if int(weekday) <= 4 else ['0']

    if request.method == 'POST':
        room_id = request.POST.get('roomId')
        start_date_str = request.POST.get('startDate')
        end_date_str = request.POST.get('endDate')
        days_raw = request.POST.get('daysOfWeek', '')
        start_time_str = request.POST.get('startTime')
        end_time_str = request.POST.get('endTime')
        purpose_type = request.POST.get('purposeType', 'TEACHING')

        try:
            room = get_object_or_404(Room, pk=room_id, is_active=True)
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            days_of_week = ','.join(d.strip() for d in days_raw.split(',') if d.strip() in ('0','1','2','3','4'))

            if not days_of_week:
                raise ValueError('กรุณาเลือกอย่างน้อยหนึ่งวัน')
            if start_date > end_date:
                raise ValueError('วันสิ้นสุดต้องไม่ก่อนวันเริ่มต้น')
            if start_time >= end_time:
                raise ValueError('เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มต้น')

            # Validate fields
            if purpose_type == 'TEACHING':
                if not request.POST.get('courseId') or not request.POST.get('courseName'):
                    raise ValueError('กรุณาระบุรหัสวิชาและชื่อวิชา')
            else:
                if not request.POST.get('topic'):
                    raise ValueError('กรุณาระบุชื่อเรื่อง/หัวข้ออบรม')

            # Conflict check
            check = start_date
            while check <= end_date:
                if str(check.weekday()) in days_of_week.split(','):
                    conflicts = Booking.objects.filter(
                        room=room, status__in=['APPROVED', 'PENDING'],
                        start_date__lte=check, end_date__gte=check,
                        start_time__lt=end_time, end_time__gt=start_time,
                    )
                    for b in conflicts:
                        if str(check.weekday()) in b.get_days_list():
                            raise ValueError(f'มีการจองห้องนี้ในช่วงเวลาดังกล่าวแล้ว (วันที่ {check})')
                check += timedelta(days=1)

            booking = Booking.objects.create(
                requester=request.user, room=room,
                purpose_type=purpose_type,
                course_id=request.POST.get('courseId') or None,
                course_name=request.POST.get('courseName') or None,
                program=request.POST.get('program') or None,
                section=request.POST.get('section') or None,
                topic=request.POST.get('topic') or None,
                start_date=start_date, end_date=end_date,
                days_of_week=days_of_week,
                start_time=start_time, end_time=end_time,
            )
            send_booking_notification_to_admin(booking)
            messages.success(request, 'ส่งคำขอจองสำเร็จ รออนุมัติจากผู้ดูแล')
            return redirect('my_bookings')

        except ValueError as e:
            for room in rooms:
                room.thumb = get_room_thumb(room)
            return render(request, 'bookings/book_room.html', {
                'rooms': rooms, 'rooms_json': rooms_json,
                'time_slots': TIME_SLOTS, 'days_of_week': DAYS_OF_WEEK,
                'programs': PROGRAMS, 'today': today,
                'selected_room_id': room_id,
                'selected_days': days_raw.split(','),
                'selected_days_json': json.dumps(days_raw.split(',')),
                'form_data': request.POST, 'error': str(e),
            })

    for room in rooms:
        room.thumb = get_room_thumb(room)
    return render(request, 'bookings/book_room.html', {
        'rooms': rooms, 'rooms_json': rooms_json,
        'time_slots': TIME_SLOTS, 'days_of_week': DAYS_OF_WEEK,
        'programs': PROGRAMS, 'today': today,
        'selected_room_id': request.GET.get('roomId', selected_room_id),
        'selected_days': selected_days,
        'selected_days_json': json.dumps(selected_days),
        'form_data': {},
    })


@login_required
@require_POST
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, requester=request.user)
    if booking.status in ('PENDING', 'APPROVED'):
        if booking.start_date <= date.today():
            messages.error(request, 'ไม่สามารถยกเลิกการจองที่ถึงหรือผ่านวันใช้งานแล้ว')
            return redirect('my_bookings')
        booking.status = 'CANCELLED'
        booking.save(update_fields=['status', 'updated_at'])
        send_booking_status_update(booking)          # แจ้งผู้จองว่าถูกยกเลิกแล้ว
        send_cancellation_notice_to_admin(booking)   # แจ้ง Admin ว่าผู้จองยกเลิกเอง
        messages.success(request, 'ยกเลิกการจองสำเร็จ ระบบส่งอีเมลแจ้งเตือนเรียบร้อย')
    return redirect('my_bookings')


@login_required
def my_bookings(request):
    status_filter = request.GET.get('status', 'all')
    qs = Booking.objects.filter(requester=request.user).select_related('room').order_by('-created_at')

    tabs = [
        {'value': 'all', 'label': 'ทั้งหมด', 'count': qs.count()},
        {'value': 'pending', 'label': 'รออนุมัติ', 'count': qs.filter(status='PENDING').count()},
        {'value': 'approved', 'label': 'อนุมัติแล้ว', 'count': qs.filter(status='APPROVED').count()},
        {'value': 'cancelled', 'label': 'ยกเลิก', 'count': qs.filter(status='CANCELLED').count()},
    ]

    if status_filter != 'all':
        qs = qs.filter(status=status_filter.upper())

    return render(request, 'bookings/my_bookings.html', {
        'bookings': qs,
        'tabs': tabs,
        'current_status': status_filter,
        'total': Booking.objects.filter(requester=request.user).count(),
        'today': date.today(),
    })


# ─── Calendar ──────────────────────────────────────────────────────────────────

@login_required
def calendar_view(request):
    room_filter = request.GET.get('room', '')
    month_str = request.GET.get('month', '')
    try:
        current = datetime.strptime(month_str + '-01', '%Y-%m-%d').date()
    except ValueError:
        current = date.today().replace(day=1)

    # Build calendar days
    first_day = current
    last_day = (current.replace(month=current.month % 12 + 1, day=1) if current.month < 12
                else current.replace(year=current.year + 1, month=1, day=1)) - timedelta(days=1)

    # Start from Sunday of first week
    start = first_day - timedelta(days=(first_day.weekday() + 1) % 7)
    end = last_day + timedelta(days=(6 - (last_day.weekday() + 1) % 7))

    bookings_qs = Booking.objects.filter(
        start_date__lte=end, end_date__gte=start,
        status__in=['APPROVED', 'PENDING']
    ).select_related('room', 'requester')
    if room_filter:
        bookings_qs = bookings_qs.filter(room_id=room_filter)

    # Build bookings by date
    bookings_by_date = {}
    b = start
    while b <= end:
        day_bks = []
        for bk in bookings_qs:
            if bk.start_date <= b <= bk.end_date and str(b.weekday()) in bk.get_days_list():
                day_bks.append(bk)
        if day_bks:
            bookings_by_date[b.isoformat()] = day_bks
        b += timedelta(days=1)

    calendar_days = []
    d = start
    while d <= end:
        bks = bookings_by_date.get(d.isoformat(), [])
        calendar_days.append({
            'date': d.isoformat(),
            'day': d.day,
            'in_month': d.month == current.month,
            'is_today': d == date.today(),
            'bookings': [{'start_time': bk.start_time.strftime('%H:%M'), 'room_code': bk.room.code, 'status': bk.status.lower()} for bk in bks[:2]],
            'more': max(0, len(bks) - 2),
        })
        d += timedelta(days=1)

    # All bookings JSON for JS
    all_bookings = []
    for bk in bookings_qs:
        d = bk.start_date
        while d <= bk.end_date:
            if str(d.weekday()) in bk.get_days_list():
                purpose = bk.course_name if bk.purpose_type == 'TEACHING' else bk.topic
                all_bookings.append({
                    'date': d.isoformat(),
                    'start_time': bk.start_time.strftime('%H:%M'),
                    'end_time': bk.end_time.strftime('%H:%M'),
                    'room_code': bk.room.code,
                    'room_name': bk.room.name,
                    'purpose': purpose or '',
                    'booker_name': bk.requester.get_full_name() or bk.requester.username,
                    'status': bk.status.lower(),
                })
            d += timedelta(days=1)

    prev_month = (current - timedelta(days=1)).strftime('%Y-%m')
    next_month = (last_day + timedelta(days=1)).strftime('%Y-%m')

    all_rooms = Room.objects.filter(is_active=True).order_by('code')
    return render(request, 'calendar/calendar.html', {
        'calendar_days': calendar_days,
        'month_label': f'{THAI_MONTHS[current.month - 1]} {current.year + 543}',
        'day_headers': ['อา', 'จ', 'อ', 'พ', 'พฤ', 'ศ', 'ส'],
        'bookings_json': json.dumps(all_bookings, ensure_ascii=False),
        'prev_month': prev_month,
        'next_month': next_month,
        'today_month': date.today().strftime('%Y-%m'),
        'all_rooms': all_rooms,
        'room_filter': room_filter,
    })


# ─── Rooms ─────────────────────────────────────────────────────────────────────

@login_required
def room_list(request):
    q = request.GET.get('q', '')
    current_size = request.GET.get('size', 'all')
    rooms = Room.objects.filter(is_active=True).order_by('code')
    if q:
        rooms = rooms.filter(name__icontains=q) | Room.objects.filter(code__icontains=q, is_active=True)
    if current_size == 'small':
        rooms = rooms.filter(capacity__lt=10)
    elif current_size == 'medium':
        rooms = rooms.filter(capacity__gte=10, capacity__lt=20)
    elif current_size == 'large':
        rooms = rooms.filter(capacity__gte=20)

    sizes = [
        {'value': 'all', 'label': 'ทั้งหมด'},
        {'value': 'small', 'label': 'เล็ก'},
        {'value': 'medium', 'label': 'กลาง'},
        {'value': 'large', 'label': 'ใหญ่'},
    ]
    for room in rooms:
        room.thumb = get_room_thumb(room)
    return render(request, 'rooms/room_list.html', {'rooms': rooms, 'q': q, 'current_size': current_size, 'sizes': sizes})


@login_required
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    recent = Booking.objects.filter(room=room).select_related('requester').order_by('-created_at')[:5]
    room.thumb = get_room_thumb(room)
    room.inroom = get_room_inroom(room)
    return render(request, 'rooms/room_detail.html', {'room': room, 'recent_bookings': recent})


@login_required
def floor_map(request):
    rooms = Room.objects.filter(is_active=True).order_by('code')
    for i, r in enumerate(rooms):
        r.mapX = 15 + (i * 16)
        r.mapY = 45
    for room in rooms:
        room.thumb = get_room_thumb(room)
        room.inroom = get_room_inroom(room)
    return render(request, 'rooms/floor_map.html', {'rooms': rooms})


# ─── AI Booking ────────────────────────────────────────────────────────────────

@login_required
def ai_booking(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST.dict()

        message = (data.get('message') or '').strip()
        if not message:
            return JsonResponse({'error': 'กรุณาพิมพ์คำขอ'}, status=400)

        if not settings.AI_API_KEY:
            return JsonResponse({'error': 'ยังไม่ได้ตั้งค่า AI_API_KEY'}, status=503)

        rooms = [{'id': str(r.id), 'code': r.code, 'name': r.name, 'capacity': r.capacity}
                 for r in Room.objects.filter(is_active=True).order_by('code')]
        today = date.today().isoformat()

        try:
            resp = requests.post(
                f"{settings.AI_API_BASE.rstrip('/')}/chat/completions",
                headers={'Authorization': f'Bearer {settings.AI_API_KEY}', 'Content-Type': 'application/json'},
                json={
                    'model': settings.AI_MODEL,
                    'messages': [
                        {'role': 'system', 'content': 'You convert Thai room booking requests to JSON. Return only JSON with keys: roomId, date (YYYY-MM-DD), start (HH:MM), end (HH:MM), attendees, purpose, reply.'},
                        {'role': 'user', 'content': json.dumps({'today': today, 'rooms': rooms, 'request': message}, ensure_ascii=False)},
                    ],
                    'temperature': 0.2, 'response_format': {'type': 'json_object'},
                },
                timeout=30,
            )
            resp.raise_for_status()
            parsed = json.loads(resp.json()['choices'][0]['message']['content'])
            return JsonResponse({'message': parsed.get('reply', 'AI เตรียมข้อมูลให้แล้ว'), 'parsed': parsed})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=502)

    suggestions = [
        'จองห้อง 406-3 พรุ่งนี้บ่าย 2-4 โมง สำหรับ 15 คน',
        'ขอห้องประชุมเล็กวันศุกร์เช้า workshop 6 คน',
    ]
    return render(request, 'bookings/ai_booking.html', {'suggestions': suggestions})


@login_required
@require_POST
def ai_confirm_booking(request):
    try:
        room = get_object_or_404(Room, pk=request.POST.get('roomId'), is_active=True)
        start_date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
        start_time = datetime.strptime(request.POST.get('startTime'), '%H:%M').time()
        end_time = datetime.strptime(request.POST.get('endTime'), '%H:%M').time()
        booking = Booking.objects.create(
            requester=request.user, room=room,
            purpose_type='TRAINING', topic=request.POST.get('purpose', 'จองผ่าน AI'),
            start_date=start_date, end_date=start_date,
            days_of_week=str(start_date.weekday()),
            start_time=start_time, end_time=end_time,
        )
        send_booking_notification_to_admin(booking)
        messages.success(request, 'AI จองห้องสำเร็จ รออนุมัติจากผู้ดูแล')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('my_bookings')


# ─── Admin ─────────────────────────────────────────────────────────────────────

def admin_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin:
            messages.error(request, 'ไม่มีสิทธิ์เข้าถึงหน้านี้')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_approval(request):
    pending = Booking.objects.filter(status='PENDING').select_related('room', 'requester').order_by('-created_at')
    recent = Booking.objects.exclude(status='PENDING').select_related('room', 'requester').order_by('-updated_at')[:10]
    all_bks = Booking.objects.all()
    stats = [
        {'label': 'รออนุมัติ', 'value': all_bks.filter(status='PENDING').count()},
        {'label': 'อนุมัติแล้ว', 'value': all_bks.filter(status='APPROVED').count()},
        {'label': 'ไม่อนุมัติ', 'value': all_bks.filter(status='REJECTED').count()},
        {'label': 'ทั้งหมด', 'value': all_bks.count()},
    ]
    return render(request, 'admin_panel/approval.html', {'pending': pending, 'recent': recent, 'stats': stats})


@admin_required
@require_POST
def review_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    action = request.POST.get('action')
    if action == 'approve':
        booking.status = 'APPROVED'
        booking.rejection_reason = ''
    elif action == 'reject':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, 'กรุณาระบุเหตุผลในการปฏิเสธ')
            return redirect('admin_approval')
        booking.status = 'REJECTED'
        booking.rejection_reason = reason
    booking.save()
    send_booking_status_update(booking)
    messages.success(request, 'อัพเดตสถานะสำเร็จ')
    return redirect('admin_approval')


@admin_required
def admin_rooms(request):
    rooms = Room.objects.all().order_by('code')
    return render(request, 'admin_panel/rooms.html', {'rooms': rooms})


@admin_required
@require_POST
def add_room(request):
    code = request.POST.get('code', '').strip()
    name = request.POST.get('name', '').strip()
    if code and name:
        Room.objects.get_or_create(code=code, defaults={
            'name': name,
            'room_type': request.POST.get('roomType', 'MEETING'),
            'capacity': int(request.POST.get('capacity', 10)),
        })
        messages.success(request, f'เพิ่มห้อง {code} สำเร็จ')
    return redirect('admin_rooms')


@admin_required
@require_POST
def edit_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    name = request.POST.get('name', '').strip()
    capacity = request.POST.get('capacity', '').strip()
    room_type = request.POST.get('roomType', room.room_type)
    if name:
        room.name = name
    if capacity.isdigit():
        room.capacity = int(capacity)
    room.room_type = room_type
    room.save()
    messages.success(request, f'แก้ไขห้อง {room.code} สำเร็จ')
    return redirect('admin_rooms')


@admin_required
@require_POST
def toggle_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    room.is_active = not room.is_active
    room.save(update_fields=['is_active'])
    messages.success(request, f'{"เปิด" if room.is_active else "ปิด"}ใช้งานห้อง {room.code} แล้ว')
    return redirect('admin_rooms')


@admin_required
def admin_reports(request):
    today = date.today()
    start_str = request.GET.get('start', today.replace(day=1).isoformat())
    end_str = request.GET.get('end', today.isoformat())
    try:
        start = datetime.strptime(start_str, '%Y-%m-%d').date()
        end = datetime.strptime(end_str, '%Y-%m-%d').date()
    except ValueError:
        start, end = today.replace(day=1), today

    approved = Booking.objects.filter(status='APPROVED', start_date__lte=end, end_date__gte=start).select_related('room', 'requester')
    total_days = max((end - start).days + 1, 1)
    total_slots = total_days * 10

    rooms = Room.objects.filter(is_active=True)
    by_room = []
    max_count = 1
    for room in rooms:
        bks = approved.filter(room=room)
        hours = sum((b.end_time.hour - b.start_time.hour) + (b.end_time.minute - b.start_time.minute) / 60 for b in bks)
        count = bks.count()
        max_count = max(max_count, count)
        by_room.append({'code': room.code, 'name': room.name, 'count': count, 'hours': round(hours, 1),
                        'utilization': round(hours / total_slots * 100, 1) if total_slots > 0 else 0})

    for r in by_room:
        r['bar_width'] = round(r['count'] / max_count * 100) if max_count > 0 else 0

    by_type = {'TEACHING': approved.filter(purpose_type='TEACHING').count(), 'TRAINING': approved.filter(purpose_type='TRAINING').count()}
    by_program = {}
    for b in approved.filter(purpose_type='TEACHING'):
        prog = b.get_program_display() if b.program else 'ไม่ระบุ'
        by_program[prog] = by_program.get(prog, 0) + 1

    total_hours = sum(r['hours'] for r in by_room)
    avg_util = round(sum(r['utilization'] for r in by_room) / len(by_room), 1) if by_room else 0

    return render(request, 'admin_panel/reports.html', {
        'start': start_str, 'end': end_str,
        'summary': {'total': approved.count(), 'hours': round(total_hours, 1), 'utilization': avg_util},
        'by_room': by_room, 'by_type': by_type, 'by_program': by_program,
    })


@admin_required
def reports_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="booking_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'ห้อง', 'ผู้จอง', 'ประเภท', 'วัตถุประสงค์', 'วันเริ่ม', 'วันสิ้นสุด', 'เวลา', 'สถานะ'])
    for b in Booking.objects.select_related('room', 'requester').order_by('-created_at'):
        purpose = b.course_name if b.purpose_type == 'TEACHING' else b.topic
        writer.writerow([b.id, f"{b.room.code} {b.room.name}", b.requester.get_full_name() or b.requester.username,
                         b.get_purpose_type_display(), purpose or '', b.start_date, b.end_date,
                         f"{b.start_time.strftime('%H:%M')}-{b.end_time.strftime('%H:%M')}", b.get_status_display()])
    return response


@admin_required
def admin_users(request):
    users = User.objects.all().order_by('username')
    return render(request, 'admin_panel/users.html', {'users': users})


@admin_required
@require_POST
def set_user_role(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    role = request.POST.get('role')
    if role in ('LECTURER', 'ADMIN'):
        user.role = role
        user.save(update_fields=['role'])
        messages.success(request, f'เปลี่ยน Role ของ {user.username} สำเร็จ')
    return redirect('admin_users')
