import calendar
from django.shortcuts import render
from bookings.models import Booking
from rooms.models import Room
from django.utils import timezone
from datetime import date, timedelta

def calendar_view(request):
    room_id = request.GET.get('room')
    rooms = Room.objects.filter(is_active=True)
    
    # Get month/year from GET or default to today
    today = timezone.localtime(timezone.now()).date()
    try:
        current_month = int(request.GET.get('month', today.month))
        current_year = int(request.GET.get('year', today.year))
    except (ValueError, TypeError):
        current_month = today.month
        current_year = today.year

    # Selected room or all if none selected
    selected_room = None
    if room_id:
        try:
            selected_room = Room.objects.get(id=room_id)
            bookings = Booking.objects.filter(room=selected_room, status__in=['APPROVED', 'PENDING'])
        except Room.DoesNotExist:
            bookings = Booking.objects.filter(status__in=['APPROVED', 'PENDING'])
    else:
        bookings = Booking.objects.filter(status__in=['APPROVED', 'PENDING'])

    # Monthly view logic using calendar module
    cal = calendar.Calendar(firstweekday=0)  # 0 = Monday
    month_days = cal.monthdays2calendar(current_year, current_month)
    
    weeks = []
    for week in month_days:
        week_days = []
        for day_num, weekday in week:
            if day_num == 0:
                week_days.append({'day': 0, 'bookings': []})
                continue
                
            day_date = date(current_year, current_month, day_num)
            day_bookings = []
            
            # Distribute bookings to this specific day
            for booking in bookings:
                if booking.start_date <= day_date <= booking.end_date:
                    if str(weekday) in booking.get_days_list():
                        day_bookings.append(booking)
            
            week_days.append({
                'day': day_num,
                'date': day_date,
                'is_today': day_date == today,
                'bookings': day_bookings
            })
        weeks.append(week_days)

    # Navigation data
    prev_month_date = date(current_year, current_month, 1) - timedelta(days=1)
    next_month_date = date(current_year, current_month, 28) + timedelta(days=5)
    
    context = {
        'rooms': rooms,
        'selected_room': selected_room,
        'weeks': weeks,
        'today': today,
        'current_month': current_month,
        'current_year': current_year,
        'month_name': calendar.month_name[current_month],
        'prev_month': prev_month_date.month,
        'prev_year': prev_month_date.year,
        'next_month': next_month_date.month,
        'next_year': next_month_date.year,
    }

    return render(request, 'calendar/calendar.html', context)
