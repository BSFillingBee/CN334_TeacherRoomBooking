import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST

from bookings.models import Booking
from bookings.utils import send_booking_notification_to_admin, send_booking_status_update
from rooms.models import Room


def _room_image(room):
    if room.image:
        return room.image.url
    capacity = room.capacity or 0
    if capacity >= 20:
        return '/static/frontend/assets/room-large.jpg'
    if capacity >= 10:
        return '/static/frontend/assets/room-medium.jpg'
    return '/static/frontend/assets/room-small.jpg'


def serialize_room(room):
    return {
        'id': str(room.id),
        'code': room.code,
        'name': room.name,
        'floor': 4,
        'capacity': room.capacity,
        'size': 'large' if room.capacity >= 20 else 'medium' if room.capacity >= 10 else 'small',
        'image': _room_image(room),
        'equipment': ['projector', 'whiteboard', 'marker'],
        'description': room.get_room_type_display(),
        'mapX': 20 + ((room.id * 13) % 60),
        'mapY': 25 + ((room.id * 17) % 50),
    }


def serialize_user(user):
    if not user.is_authenticated:
        return None

    full_name = user.get_full_name() or user.username
    initials = ''.join(part[:1] for part in full_name.split()[:2]) or user.username[:2]
    return {
        'name': full_name,
        'email': user.email or '',
        'department': 'คณะวิศวกรรมศาสตร์',
        'role': 'admin' if getattr(user, 'is_admin', False) else 'staff',
        'avatar': initials.upper(),
    }


def serialize_booking(booking):
    purpose = booking.course_name if booking.purpose_type == 'TEACHING' else booking.topic
    if not purpose:
        purpose = booking.course_id or booking.get_purpose_type_display()

    requester_name = booking.requester.get_full_name() or booking.requester.username
    return {
        'id': str(booking.id),
        'roomId': str(booking.room_id),
        'bookerName': requester_name,
        'bookerEmail': booking.requester.email or '',
        'department': 'คณะวิศวกรรมศาสตร์',
        'purpose': purpose,
        'date': booking.start_date.isoformat(),
        'startTime': booking.start_time.strftime('%H:%M'),
        'endTime': booking.end_time.strftime('%H:%M'),
        'attendees': booking.room.capacity,
        'status': booking.status.lower(),
        'createdAt': timezone.localtime(booking.created_at).date().isoformat(),
    }


def bootstrap_payload(request):
    bookings = Booking.objects.select_related('room', 'requester')
    if request.user.is_authenticated and not getattr(request.user, 'is_admin', False):
        bookings = bookings.filter(requester=request.user)

    return {
        'csrfToken': get_token(request),
        'isAuthenticated': request.user.is_authenticated,
        'currentUser': serialize_user(request.user),
        'rooms': [serialize_room(room) for room in Room.objects.filter(is_active=True).order_by('code')],
        'bookings': [serialize_booking(booking) for booking in bookings.order_by('-created_at')[:200]],
    }


@ensure_csrf_cookie
def frontend_app(request):
    return render(request, 'frontend.html', {'bootstrap_json': json.dumps(bootstrap_payload(request), ensure_ascii=False)})


dashboard = frontend_app


@require_http_methods(['GET'])
def api_bootstrap(request):
    return JsonResponse(bootstrap_payload(request))


@require_POST
def api_login(request):
    data = json.loads(request.body or '{}')
    user = authenticate(request, username=data.get('username'), password=data.get('password'))
    if user is None:
        return JsonResponse({'error': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'}, status=400)

    login(request, user)
    return JsonResponse(bootstrap_payload(request))


@require_POST
def api_logout(request):
    logout(request)
    return JsonResponse({'ok': True})


@login_required
@require_POST
def api_booking_create(request):
    data = json.loads(request.body or '{}')
    room = get_object_or_404(Room, pk=data.get('roomId'), is_active=True)
    start_date = timezone.datetime.strptime(data.get('date'), '%Y-%m-%d').date()
    start_time = timezone.datetime.strptime(data.get('startTime'), '%H:%M').time()
    end_time = timezone.datetime.strptime(data.get('endTime'), '%H:%M').time()
    day = str(start_date.weekday())

    conflicts = Booking.objects.filter(
        room=room,
        status__in=['APPROVED', 'PENDING'],
        start_date__lte=start_date,
        end_date__gte=start_date,
        start_time__lt=end_time,
        end_time__gt=start_time,
    )
    if any(day in booking.get_days_list() for booking in conflicts):
        return JsonResponse({'error': 'มีการจองห้องนี้ในช่วงเวลาดังกล่าวแล้ว'}, status=409)

    booking = Booking.objects.create(
        requester=request.user,
        room=room,
        purpose_type='TRAINING',
        topic=data.get('purpose') or 'จองห้องประชุม',
        start_date=start_date,
        end_date=start_date,
        days_of_week=day,
        start_time=start_time,
        end_time=end_time,
    )
    send_booking_notification_to_admin(booking)
    return JsonResponse({'booking': serialize_booking(booking)}, status=201)


@login_required
@require_POST
def api_booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, requester=request.user)
    if booking.status not in ['PENDING', 'APPROVED']:
        return JsonResponse({'error': 'ไม่สามารถยกเลิกการจองนี้ได้'}, status=400)

    booking.status = 'CANCELLED'
    booking.save(update_fields=['status', 'updated_at'])
    send_booking_status_update(booking)
    return JsonResponse({'booking': serialize_booking(booking)})


@login_required
@require_POST
def api_booking_review(request, pk):
    if not getattr(request.user, 'is_admin', False):
        return JsonResponse({'error': 'ไม่มีสิทธิ์ใช้งาน'}, status=403)

    data = json.loads(request.body or '{}')
    action = data.get('action')
    booking = get_object_or_404(Booking, pk=pk)
    if action == 'approve':
        booking.status = 'APPROVED'
    elif action == 'reject':
        booking.status = 'REJECTED'
        booking.rejection_reason = data.get('reason', '')
    else:
        return JsonResponse({'error': 'action ไม่ถูกต้อง'}, status=400)

    booking.save()
    send_booking_status_update(booking)
    return JsonResponse({'booking': serialize_booking(booking)})
