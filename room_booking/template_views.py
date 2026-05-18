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
TIME_SLOTS = ['08:00','08:30','09:00','09:30','10:00','10:30','11:00','11:30','12:00','12:30','13:00','13:30','14:00','14:30','15:00','15:30','16:00','16:30','17:00','17:30','18:00']
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
# Multiple images per room (list)
ROOM_IMAGES = {
    '406-3':   ['images/rooms/406-3.jpg', 'images/rooms/inroom406-3(1).jpg', 'images/rooms/inroom406-3(2).jpg'],
    '406-5':   ['images/rooms/406-5.jpg', 'images/rooms/inroom406-5(1).jpg'],
    '408-1':   ['images/rooms/408-1.jpg', 'images/rooms/inroom408-1(1).jpg'],
    '408-2/1': ['images/rooms/408-2_1.jpg', 'images/rooms/inroom408-2_1(1).jpg'],
    '408-2/2': ['images/rooms/408-2_2.jpg', 'images/rooms/inroom408-2_2(1).jpg', 'images/rooms/inroom408-2_2(2).jpg'],
}
# Equipment per room
ROOM_EQUIPMENT = {
    '406-3':   ['โปรเจกเตอร์', 'ไวท์บอร์ด', 'ระบบเสียง', 'แอร์', 'Wi-Fi'],
    '406-5':   ['โปรเจกเตอร์', 'ไวท์บอร์ด', 'แอร์', 'Wi-Fi'],
    '408-1':   ['โปรเจกเตอร์', 'ไวท์บอร์ด', 'แอร์', 'Wi-Fi'],
    '408-2/1': ['โปรเจกเตอร์', 'ไวท์บอร์ด', 'แอร์', 'Wi-Fi'],
    '408-2/2': ['โปรเจกเตอร์', 'ไวท์บอร์ด', 'แอร์', 'Wi-Fi'],
}

def get_room_thumb(room):
    return ROOM_THUMB.get(room.code, '')

def get_room_images(room):
    return ROOM_IMAGES.get(room.code, [])

def get_room_equipment(room):
    return ROOM_EQUIPMENT.get(room.code, [])


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = None
    next_url = request.GET.get('next', '') or request.POST.get('next', '')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if request.POST.get('remember_me'):
                request.session.set_expiry(getattr(settings, 'REMEMBER_ME_SESSION_AGE', 30 * 24 * 60 * 60))
            else:
                request.session.set_expiry(getattr(settings, 'SESSION_COOKIE_AGE', 8 * 60 * 60))
            if next_url:
                return redirect(next_url)
            return redirect('admin_approval' if user.is_admin else 'dashboard')
        error = 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'
    return render(request, 'accounts/login.html', {'error': error, 'next': next_url})


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
    requested_start = request.GET.get('startDate') or today
    requested_end = request.GET.get('endDate') or requested_start
    try:
        initial_start_date = datetime.strptime(requested_start, '%Y-%m-%d').date()
    except ValueError:
        initial_start_date = date.today()
        requested_start = initial_start_date.isoformat()
    try:
        initial_end_date = datetime.strptime(requested_end, '%Y-%m-%d').date()
    except ValueError:
        initial_end_date = initial_start_date
        requested_end = initial_end_date.isoformat()
    if initial_end_date < initial_start_date:
        initial_end_date = initial_start_date
        requested_end = requested_start

    weekday = str(initial_start_date.weekday())
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
            selected_day_values = [d.strip() for d in days_raw.split(',') if d.strip() in ('0', '1', '2', '3', '4')]
            days_of_week = ','.join(selected_day_values)

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
                'initial_start_date': start_date_str or today,
                'initial_end_date': end_date_str or start_date_str or today,
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
        'initial_start_date': requested_start,
        'initial_end_date': requested_end,
        'selected_room_id': request.GET.get('roomId', selected_room_id),
        'selected_days': selected_days,
        'selected_days_json': json.dumps(selected_days),
        'form_data': request.GET,
    })


@login_required
@require_POST
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, requester=request.user)
    if booking.status in ('PENDING', 'APPROVED'):
        if booking.status == 'APPROVED' and booking.start_date <= date.today():
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
    current_type = request.GET.get('type', 'all')
    rooms = Room.objects.filter(is_active=True).order_by('code')
    if q:
        rooms = rooms.filter(name__icontains=q) | Room.objects.filter(code__icontains=q, is_active=True)
    if current_type == 'MEETING':
        rooms = rooms.filter(room_type='MEETING')
    elif current_type == 'LECTURE':
        rooms = rooms.filter(room_type='LECTURE')

    room_types = [
        {'value': 'all', 'label': 'ทั้งหมด'},
        {'value': 'MEETING', 'label': 'ห้องประชุม'},
        {'value': 'LECTURE', 'label': 'ห้องบรรยาย'},
    ]
    for room in rooms:
        room.thumb = get_room_thumb(room)
    return render(request, 'rooms/room_list.html', {'rooms': rooms, 'q': q, 'current_type': current_type, 'room_types': room_types})


@login_required
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    recent = Booking.objects.filter(room=room).select_related('requester').order_by('-created_at')[:5]
    room.thumb = get_room_thumb(room)
    room_images = get_room_images(room)
    room_equipment = get_room_equipment(room)
    return render(request, 'rooms/room_detail.html', {
        'room': room,
        'recent_bookings': recent,
        'room_images': room_images,
        'room_equipment': room_equipment,
    })


@login_required
def floor_map(request):
    # Room positions on the floor plan image (left%, top%)
    # Based on ECE Building 3 Floor 4 map
    ROOM_POSITIONS = {
        '406':   (62, 83), '406-1': (59, 83), '406-2': (55, 83),
        '406-3': (56, 73), '406-4': (63, 73),
        '406-5': (70, 67), '406-6': (64, 67), '406-7': (57, 67),
        '407':   (49, 88), '408':   (26, 88),
        '408-1': (36, 78), '408-2': (28, 78), '408-3': (19, 78),
        '408-4': (19, 93), '408-5': (28, 93), '408-6': (36, 93),
        '409':   (20, 68),
        '410':   (25, 52), '410-1': (37, 47), '410-2': (28, 47), '410-3': (19, 47),
        '410-4': (19, 57), '410-5': (28, 57), '410-6': (37, 57),
        '411':   (22, 35),
        '411-1': (37, 40), '411-2': (28, 40), '411-3': (19, 40),
        '411-4': (19, 28), '411-5': (28, 28), '411-6': (37, 28),
        '412':   (20, 14),
        '412-1': (42, 9),  '412-2': (33, 9),  '412-3': (24, 9),  '412-4': (15, 9),
        '412-5': (15, 15), '412-6': (15, 21), '412-7': (15, 27),
        '412-8': (37, 20), '412-9': (37, 14),
        '416':   (44, 17),
        '418':   (72, 14),
        '418-1': (57, 25), '418-2': (67, 25),
        '418-3': (84, 25), '418-4': (84, 17), '418-5': (84, 11),
        '418-6': (84, 6),  '418-7': (76, 6),  '418-8': (67, 6),  '418-9': (58, 6),
        '418-10':(60, 17), '418-11':(68, 17),
        '420':   (72, 33), '421':   (72, 46), '422':   (72, 60),
        '422-1': (58, 63), '422-2': (65, 63),
        '422-3': (65, 56), '422-4': (58, 56),
    }
    rooms = Room.objects.filter(is_active=True).order_by('code')
    for i, room in enumerate(rooms):
        pos = ROOM_POSITIONS.get(room.code, (10 + (i % 10)*8, 20 + (i//10)*20))
        room.mapX = pos[0]
        room.mapY = pos[1]
        room.thumb = get_room_thumb(room)
        imgs = get_room_images(room)
        room.inroom = imgs[0] if imgs else ''
    return render(request, 'rooms/floor_map.html', {'rooms': rooms})


# ─── AI Booking ────────────────────────────────────────────────────────────────

def _extract_json_object(text):
    text = (text or '').strip()
    if text.startswith('```'):
        text = text.strip('`')
        if text.startswith('json'):
            text = text[4:].strip()
            
    text = text.strip()
    
    # Try parsing the whole string first
    try:
        return json.loads(text)
    except Exception:
        pass
        
    decoder = json.JSONDecoder()
    objects = []
    idx = 0
    while idx < len(text):
        while idx < len(text) and text[idx].isspace():
            idx += 1
        if idx >= len(text):
            break
        try:
            obj, end_idx = decoder.raw_decode(text[idx:])
            objects.append(obj)
            idx += end_idx
        except json.JSONDecodeError:
            next_brace = text.find('{', idx)
            if next_brace == -1:
                break
            if next_brace == idx:
                idx += 1
            else:
                idx = next_brace
            
    if not objects:
        # Fallback to the old method
        start = text.find('{')
        end = text.rfind('}')
        if start >= 0 and end >= start:
            try:
                return json.loads(text[start:end + 1])
            except Exception:
                pass
        return {}
        
    # Merge all dictionaries found
    merged = {}
    for obj in objects:
        if isinstance(obj, dict):
            merged.update(obj)
            
    return merged


def _resolve_room(value):
    raw = str(value or '').strip()
    if not raw:
        raise ValueError('AI ยังไม่ได้ระบุห้อง')
    room = None
    if raw.isdigit():
        room = Room.objects.filter(pk=int(raw), is_active=True).first()
    if room is None:
        room = Room.objects.filter(code__iexact=raw, is_active=True).first()
    if room is None:
        raise ValueError(f'ไม่พบห้อง {raw}')
    return room


def _validate_ai_booking(parsed):
    room = _resolve_room(parsed.get('roomId') or parsed.get('roomCode') or parsed.get('room'))
    booking_date = datetime.strptime(str(parsed.get('date')), '%Y-%m-%d').date()
    start_time = datetime.strptime(str(parsed.get('start')), '%H:%M').time()
    end_time = datetime.strptime(str(parsed.get('end')), '%H:%M').time()
    if start_time >= end_time:
        raise ValueError('เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มต้น')
    has_selected_day_in_range = False
    check = start_date
    while check <= end_date:
        if str(check.weekday()) in selected_day_values:
            has_selected_day_in_range = True
            break
        check += timedelta(days=1)
        if not has_selected_day_in_range:
            raise ValueError('วันที่เลือกไม่อยู่ในช่วงวันที่เริ่มต้นและสิ้นสุด')
    conflicts = Booking.objects.filter(
        room=room, status__in=['APPROVED', 'PENDING'],
        start_date__lte=booking_date, end_date__gte=booking_date,
        start_time__lt=end_time, end_time__gt=start_time,
    )
    for booking in conflicts:
        if str(booking_date.weekday()) in booking.get_days_list():
            raise ValueError(f'ห้อง {room.code} มีการจองในช่วงเวลานี้แล้ว')

    parsed['roomId'] = str(room.id)
    parsed['roomCode'] = room.code
    parsed['roomName'] = room.name
    parsed['date'] = booking_date.isoformat()
    parsed['start'] = start_time.strftime('%H:%M')
    parsed['end'] = end_time.strftime('%H:%M')
    parsed['attendees'] = parsed.get('attendees') or ''
    parsed['purpose'] = (parsed.get('purpose') or 'จองผ่าน AI').strip()
    return parsed

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
        today = timezone.localdate().isoformat()

        try:
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL}:generateContent?key={settings.AI_API_KEY}"
            
            # Build per-room schedule context: expand recurring bookings into individual date occurrences
            from datetime import date as _date
            today_date = timezone.localdate()
            # Look ahead 60 days
            lookahead = today_date + timedelta(days=60)
            upcoming_bookings = Booking.objects.filter(
                end_date__gte=today_date,
                start_date__lte=lookahead,
                status__in=['APPROVED', 'PENDING']
            ).select_related('room').order_by('start_date', 'start_time')
            
            # Build per-room dict of { date_str: [(start, end), ...] }
            room_schedule = {}
            for b in upcoming_bookings:
                rcode = b.room.code
                if rcode not in room_schedule:
                    room_schedule[rcode] = {}
                occurrence_dates = b.get_occurrence_dates()
                for occ_date in occurrence_dates:
                    if occ_date < today_date:
                        continue
                    d_str = occ_date.isoformat()
                    room_schedule[rcode].setdefault(d_str, []).append(
                        f"{b.start_time.strftime('%H:%M')}-{b.end_time.strftime('%H:%M')}"
                    )

            # Build readable context for AI
            rooms_with_schedule = []
            for r in Room.objects.filter(is_active=True).order_by('code'):
                schedule = room_schedule.get(r.code, {})
                rooms_with_schedule.append({
                    'id': str(r.id), 'code': r.code, 'name': r.name,
                    'capacity': r.capacity, 'type': r.room_type,
                    'booked_slots': schedule  # { '2026-05-18': ['09:30-12:30', '14:00-16:00'], ... }
                })

            system_instruction = (
                "You are an AI assistant for ECE Thammasat's room booking system.\n"
                "You help users check room availability and create bookings.\n"
                "ALWAYS return a SINGLE JSON object.\n"
                "CRITICAL: You MUST ALWAYS reply in Thai language in the 'reply' field. Never reply in English.\n"
                "If the user wants to book, you MUST collect: roomId (or roomCode), date (YYYY-MM-DD), start time (HH:MM), end time (HH:MM), attendees, and purpose.\n"
                "CRITICAL: A 'Current Booking State' JSON will be provided in the user prompt. You MUST carry over ALL fields from it into your JSON response exactly as they are, unless the user explicitly updates them. Do not drop any fields.\n"
                "CRITICAL: You MUST extract and include EVERY piece of booking information the user mentions (roomId/roomCode, date, start, end, attendees, purpose) in the JSON immediately, even if the booking is not yet complete. Never leave a field empty if the user has provided it.\n"
                "CRITICAL: If any required booking information is missing, ask the user ONLY for the specific information that is missing in the 'reply' field. Do NOT ask for information you already have.\n"
                "CRITICAL: If you have gathered ALL required booking information (room, date, start, end), your 'reply' MUST instruct the user to click the confirmation button below to complete the booking (e.g., 'ข้อมูลครบถ้วนแล้ว กรุณากดปุ่ม ยืนยันการจอง ด้านล่างได้เลยครับ'). Do NOT ask them a yes/no question like 'ใช่หรือไม่'.\n"
                "AVAILABILITY RULES:\n"
                "- Each room has a 'booked_slots' dict: {date: [list of occupied time ranges]}.\n"
                "- A room is FULLY AVAILABLE on a date if that date does not appear in booked_slots.\n"
                "- A room is PARTIALLY AVAILABLE if the date appears but the user's requested time does NOT overlap any booked slot.\n"
                "  Two time ranges overlap if: request_start < booked_end AND request_end > booked_start.\n"
                "- A room is UNAVAILABLE for the user's specific time if their requested window overlaps with a booked slot.\n"
                "WHEN ASKED ABOUT ROOM AVAILABILITY:\n"
                "- ALWAYS list ALL rooms from the Rooms list in your reply.\n"
                "- For each room, state whether it is: (a) ว่างทั้งวัน (fully free), (b) ว่างบางช่วงเวลา + list occupied slots (partially booked), or (c) ไม่ว่าง for the specific requested time.\n"
                "- If the user asks about a specific time, check overlaps precisely and tell them which rooms are free at that time.\n"
                "- NEVER say a room is 'ไม่ว่าง' (unavailable) for the whole day if it only has partial bookings — always clarify the occupied time slots so the user can book other time slots.\n"
                "Thai time hints: บ่าย 2 = 14:00, เช้า 9 = 09:00, บ่าย 2-4 โมง = start 14:00 end 16:00, เช้า = 08:00-12:00, บ่าย = 13:00-17:00.\n\n"
                f"=== SYSTEM CONTEXT ===\n"
                f"Today is {today}\n"
                f"Rooms (with booked_slots per date): {json.dumps(rooms_with_schedule, ensure_ascii=False)}\n"
                "====================\n"
            )
            
            history = data.get('history', [])
            contents = []
            
            # Build current accumulated state from history
            current_state = {}
            for msg in history:
                if msg.get('role') == 'model':
                    try:
                        parsed_msg = _extract_json_object(msg['parts'][0]['text'])
                        for k, v in parsed_msg.items():
                            if k != 'reply' and v:
                                current_state[k] = v
                    except Exception:
                        pass

            # Copy conversation history verbatim
            for msg in history:
                contents.append(msg)
                
            # Append the current user message with the current state
            contents.append({
                "role": "user",
                "parts": [{"text": f"Current Booking State: {json.dumps(current_state)}\n\nUser: {message}"}]
            })

            payload = {
                "systemInstruction": {
                    "parts": [{"text": system_instruction}]
                },
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.2,
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "type": "OBJECT",
                        "properties": {
                            "roomId": {"type": "STRING", "description": "ID of the room. Empty string if unknown."},
                            "roomCode": {"type": "STRING", "description": "Code of the room. Empty string if unknown."},
                            "date": {"type": "STRING", "description": "Date in YYYY-MM-DD. Empty string if unknown."},
                            "start": {"type": "STRING", "description": "Start time in HH:MM. Empty string if unknown."},
                            "end": {"type": "STRING", "description": "End time in HH:MM. Empty string if unknown."},
                            "attendees": {"type": "STRING", "description": "Number of attendees. Empty string if unknown."},
                            "purpose": {"type": "STRING", "description": "Purpose of booking. Empty string if unknown."},
                            "reply": {"type": "STRING", "description": "Your response to the user in Thai"}
                        },
                        "required": ["roomId", "roomCode", "date", "start", "end", "attendees", "purpose", "reply"]
                    }
                }
            }

            resp = requests.post(api_url, headers={'Content-Type': 'application/json'}, json=payload, timeout=30)
            
            if resp.status_code != 200:
                try:
                    err_detail = resp.json()
                    error_msg = f"AI Error ({resp.status_code}): {err_detail.get('error', {}).get('message', resp.text)}"
                except:
                    error_msg = f"AI Error ({resp.status_code}): {resp.text}"
                return JsonResponse({'error': error_msg}, status=resp.status_code)

            # การดึงข้อมูลจาก Native API จะใช้โครงสร้างนี้ครับ
            ai_text = resp.json()['candidates'][0]['content']['parts'][0]['text']
            parsed = _extract_json_object(ai_text)
            
            # Merge current state back into parsed if AI dropped any fields
            for k, v in current_state.items():
                if k not in parsed or not parsed[k]:
                    parsed[k] = v
            
            # ตรวจสอบว่าเป็นการพยายามจองห้องหรือไม่ (ถ้ามีข้อมูลครบถ้วนถือว่าเป็นการจอง)
            has_room = any(k in parsed and parsed[k] for k in ('roomId', 'roomCode', 'room'))
            is_booking_request = has_room and parsed.get('date') and parsed.get('start') and parsed.get('end')
            
            if is_booking_request:
                parsed = _validate_ai_booking(parsed)
                
            return JsonResponse({'message': parsed.get('reply', 'AI เตรียมข้อมูลให้แล้ว'), 'parsed': parsed})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=502)

    suggestions = [
        'จองห้อง 406-3 พรุ่งนี้บ่าย 2-4 โมง สำหรับ 15 คน เพื่อประชุมงาน',
        'ห้องไหนว่างวันพรุ่งนี้บ้าง?',
        'ขอดูห้องประชุมที่ว่างช่วงเช้าวันศุกร์นี้',
    ]
    return render(request, 'bookings/ai_booking.html', {'suggestions': suggestions})


@login_required
@require_POST
def ai_confirm_booking(request):
    try:
        parsed = {
            'roomId': request.POST.get('roomId'),
            'date': request.POST.get('date'),
            'start': request.POST.get('startTime'),
            'end': request.POST.get('endTime'),
            'purpose': request.POST.get('purpose'),
        }
        parsed = _validate_ai_booking(parsed)
        room = get_object_or_404(Room, pk=parsed['roomId'], is_active=True)
        start_date = datetime.strptime(parsed['date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(parsed['start'], '%H:%M').time()
        end_time = datetime.strptime(parsed['end'], '%H:%M').time()
        booking = Booking.objects.create(
            requester=request.user, room=room,
            purpose_type='TRAINING', topic=parsed['purpose'],
            start_date=start_date, end_date=start_date,
            days_of_week=str(start_date.weekday()),
            start_time=start_time, end_time=end_time,
        )
        send_booking_notification_to_admin(booking)
        messages.success(request, 'AI จองห้องสำเร็จ รออนุมัติจากผู้ดูแล')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('my_bookings')


# ─── Admin AI ─────────────────────────────────────────────────────────────────

@login_required
def admin_ai_page(request):
    """Render the dedicated Admin AI chat page."""
    if not request.user.is_admin:
        messages.error(request, 'ไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('dashboard')
    return render(request, 'admin_panel/ai_chat.html')


@login_required
def admin_ai_chat(request):
    """AI chat API endpoint for admin: list pending bookings and bulk approve."""
    if not request.user.is_admin:
        return JsonResponse({'error': 'ไม่มีสิทธิ์'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST.dict()

    message = (data.get('message') or '').strip()
    if not message:
        return JsonResponse({'error': 'กรุณาพิมพ์คำสั่ง'}, status=400)

    if not settings.AI_API_KEY:
        return JsonResponse({'error': 'ยังไม่ได้ตั้งค่า AI_API_KEY'}, status=503)

    # Build pending bookings context for admin
    pending_bookings = Booking.objects.filter(status='PENDING').select_related('room', 'requester').order_by('-created_at')
    pending_context = [
        {
            'id': str(b.id),
            'room_code': b.room.code, 'room_name': b.room.name,
            'requester': b.requester.get_full_name() or b.requester.username,
            'email': b.requester.email,
            'purpose': b.course_name if b.purpose_type == 'TEACHING' else b.topic,
            'purpose_type': b.get_purpose_type_display(),
            'dates': b.occurrence_dates_display,
            'time': f"{b.start_time.strftime('%H:%M')}-{b.end_time.strftime('%H:%M')}",
            'status': 'รออนุมัติ',
        }
        for b in pending_bookings
    ]

    today = timezone.localdate().isoformat()
    try:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL}:generateContent?key={settings.AI_API_KEY}"
        system_instruction = (
            "You are an AI assistant for an admin in ECE Thammasat's room booking system.\n"
            "ALWAYS return a SINGLE JSON object with fields: 'reply' (Thai string) and 'action' (string, one of: 'none', 'approve_all', 'approve_ids').\n"
            "If action is 'approve_ids', also include 'ids': list of booking ID strings to approve.\n"
            "CRITICAL: Always reply in Thai language in the 'reply' field.\n"
            "You can help admin:\n"
            "1. List all pending bookings with details.\n"
            "2. Approve all pending bookings (set action='approve_all').\n"
            "3. Approve specific bookings by ID (set action='approve_ids', ids=[...]).\n"
            "4. Provide summary statistics.\n"
            "When listing bookings, format them clearly showing ID, room, requester, purpose, dates, and time.\n"
            "If admin says to approve all, set action='approve_all'.\n"
            "If admin says to approve specific ones (by name, room, or ID), set action='approve_ids' with the matching IDs.\n"
            f"=== ADMIN CONTEXT ===\n"
            f"Today is {today}\n"
            f"Pending Bookings ({len(pending_context)} total): {json.dumps(pending_context, ensure_ascii=False)}\n"
            "===================\n"
        )

        history = data.get('history', [])
        contents = list(history)
        contents.append({"role": "user", "parts": [{"text": message}]})

        payload = {
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "contents": contents,
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "OBJECT",
                    "properties": {
                        "reply": {"type": "STRING"},
                        "action": {"type": "STRING"},
                        "ids": {"type": "ARRAY", "items": {"type": "STRING"}},
                    },
                    "required": ["reply", "action"]
                }
            }
        }

        resp = requests.post(api_url, headers={'Content-Type': 'application/json'}, json=payload, timeout=30)
        if resp.status_code != 200:
            try:
                err_detail = resp.json()
                error_msg = f"AI Error ({resp.status_code}): {err_detail.get('error', {}).get('message', resp.text)}"
            except Exception:
                error_msg = f"AI Error ({resp.status_code}): {resp.text}"
            return JsonResponse({'error': error_msg}, status=resp.status_code)

        ai_text = resp.json()['candidates'][0]['content']['parts'][0]['text']
        parsed = _extract_json_object(ai_text)
        action = parsed.get('action', 'none')
        approved_count = 0

        if action == 'approve_all':
            approved_count = pending_bookings.count()
            for b in pending_bookings:
                b.status = 'APPROVED'
                b.save(update_fields=['status', 'updated_at'])
                try:
                    send_booking_status_update(b)
                except Exception:
                    pass
        elif action == 'approve_ids':
            ids_to_approve = [str(i) for i in (parsed.get('ids') or [])]
            for bid in ids_to_approve:
                try:
                    b = Booking.objects.get(pk=int(bid), status='PENDING')
                    b.status = 'APPROVED'
                    b.save(update_fields=['status', 'updated_at'])
                    approved_count += 1
                    try:
                        send_booking_status_update(b)
                    except Exception:
                        pass
                except Booking.DoesNotExist:
                    pass

        return JsonResponse({
            'message': parsed.get('reply', 'เสร็จสิ้น'),
            'action': action,
            'approved_count': approved_count,
            'pending_count': Booking.objects.filter(status='PENDING').count(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=502)



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