from django.shortcuts import render
from bookings.models import Booking
from rooms.models import Room
from django.utils import timezone
import datetime

def calendar_view(request):
    room_id = request.GET.get('room')
    rooms = Room.objects.filter(is_active=True)
    
    # Selected room or all if none selected
    selected_room = None
    if room_id:
        selected_room = Room.objects.get(id=room_id)
        bookings = Booking.objects.filter(room=selected_room, status__in=['APPROVED', 'PENDING'])
    else:
        bookings = Booking.objects.filter(status__in=['APPROVED', 'PENDING'])

    # Weekly view logic
    # Get current week start (Monday)
    today = timezone.now().date()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    
    days = []
    for i in range(7):
        day_date = start_of_week + datetime.timedelta(days=i)
        days.append({
            'date': day_date,
            'name': day_date.strftime('%A'),
            'bookings': []
        })

    # Distribute bookings to days
    for booking in bookings:
        # Check if booking date range covers the current week
        # And if the specific weekday is in booking.days_of_week
        for day in days:
            if booking.start_date <= day['date'] <= booking.end_date:
                weekday_index = str(day['date'].weekday())
                if weekday_index in booking.get_days_list():
                    day['bookings'].append(booking)

    return render(request, 'calendar/calendar.html', {
        'rooms': rooms,
        'selected_room': selected_room,
        'days': days,
        'today': today
    })
