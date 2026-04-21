from django.shortcuts import render
from bookings.models import Booking
from rooms.models import Room
from django.db.models import Count, Sum
from django.contrib.auth.decorators import login_required
import datetime

@login_required
def report_dashboard(request):
    if not request.user.is_admin:
        return redirect('dashboard')

    # Get room stats
    rooms = Room.objects.all()
    room_stats = []
    
    for room in rooms:
        bookings = Booking.objects.filter(room=room, status='APPROVED')
        count = bookings.count()
        
        # Calculate total hours (simplified)
        total_seconds = 0
        for b in bookings:
            start = datetime.datetime.combine(datetime.date.today(), b.start_time)
            end = datetime.datetime.combine(datetime.date.today(), b.end_time)
            # Find how many days this booking covers
            days_count = len(b.get_days_list())
            # For simplicity, calculate duration * days
            duration = (end - start).total_seconds()
            total_seconds += duration * days_count
            
        total_hours = total_seconds / 3600
        
        # Utilization Rate (assuming 8 hours per day, 5 days a week = 40 hours/week)
        # We can calculate based on a 4-week month (160 hours)
        utilization = (total_hours / 160) * 100 if total_hours > 0 else 0
        
        room_stats.append({
            'room': room,
            'count': count,
            'hours': round(total_hours, 1),
            'utilization': round(utilization, 1)
        })

    return render(request, 'reports/report_main.html', {
        'room_stats': room_stats
    })
