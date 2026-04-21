from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking
from .forms import BookingForm
from django.db.models import Q
from .utils import send_booking_notification_to_admin, send_booking_status_update

@login_required
def booking_create(request):
    room_id = request.GET.get('room')
    initial_data = {}
    if room_id:
        initial_data['room'] = room_id

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.requester = request.user
            
            # Combine selected days into comma-separated string
            selected_days = form.cleaned_data.get('selected_days')
            booking.days_of_week = ','.join(selected_days)
            
            # Conflict Detection
            conflicts = Booking.objects.filter(
                room=booking.room,
                status='APPROVED',
                start_date__lte=booking.end_date,
                end_date__gte=booking.start_date,
                start_time__lt=booking.end_time,
                end_time__gt=booking.start_time
            )
            
            # Refined check for days_of_week intersection
            has_conflict = False
            for existing in conflicts:
                existing_days = set(existing.get_days_list())
                new_days = set(selected_days)
                if existing_days.intersection(new_days):
                    has_conflict = True
                    break
            
            if has_conflict:
                messages.error(request, "ไม่สามารถจองได้ เนื่องจากมีการจองห้องนี้ในช่วงเวลาดังกล่าวแล้ว")
            else:
                booking.save()
                send_booking_notification_to_admin(booking)
                messages.success(request, "บันทึกการจองสำเร็จ กรุณารอการอนุมัติจากเจ้าหน้าที่")
                return redirect('booking_list')
    else:
        form = BookingForm(initial=initial_data)
        
    return render(request, 'bookings/booking_form.html', {'form': form})

@login_required
def booking_list(request):
    bookings = Booking.objects.filter(requester=request.user)
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})

@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, requester=request.user)
    
    # Allow cancelling PENDING or APPROVED bookings
    if booking.status in ['PENDING', 'APPROVED']:
        old_status = booking.status
        booking.status = 'CANCELLED'
        booking.save()
        print(f"DEBUG: Booking {pk} status changed from {old_status} to CANCELLED")
        messages.success(request, "ยกเลิกการจองเรียบร้อยแล้ว")
    else:
        print(f"DEBUG: Booking {pk} cannot be cancelled. Current status: {booking.status}")
        messages.error(request, "ไม่สามารถยกเลิกการจองที่ดำเนินการไปแล้ว (ปฏิเสธ/ยกเลิกแล้ว) ได้")
        
    return redirect('booking_list')

# Admin Views
@login_required
def admin_approval_list(request):
    if not request.user.is_admin:
        messages.error(request, "เฉพาะเจ้าหน้าที่เท่านั้นที่เข้าถึงหน้านี้ได้")
        return redirect('dashboard')
    
    pending_bookings = Booking.objects.filter(status='PENDING').order_by('created_at')
    history_bookings = Booking.objects.exclude(status='PENDING').order_by('-updated_at')[:20]
    
    return render(request, 'bookings/admin_approvals.html', {
        'pending_bookings': pending_bookings,
        'history_bookings': history_bookings
    })

@login_required
def admin_approve_reject(request, pk):
    if not request.user.is_admin:
        return redirect('dashboard')
        
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        reason = request.POST.get('reason', '')
        
        if action == 'approve':
            booking.status = 'APPROVED'
            messages.success(request, f"อนุมัติการจองห้อง {booking.room.code} เรียบร้อยแล้ว")
        elif action == 'reject':
            booking.status = 'REJECTED'
            booking.rejection_reason = reason
            messages.success(request, f"ปฏิเสธการจองห้อง {booking.room.code} เรียบร้อยแล้ว")
            
        booking.save()
        send_booking_status_update(booking)
        
    return redirect('admin_approval_list')
