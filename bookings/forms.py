from django import forms
from .models import Booking
from rooms.models import Room

class BookingForm(forms.ModelForm):
    DAYS_CHOICES = (
        ('0', 'วันจันทร์'),
        ('1', 'วันอังคาร'),
        ('2', 'วันพุธ'),
        ('3', 'วันพฤหัสบดี'),
        ('4', 'วันศุกร์'),
    )
    
    selected_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='วันที่ใช้งานในสัปดาห์ (จันทร์-ศุกร์)',
        required=True
    )

    class Meta:
        model = Booking
        fields = [
            'room', 'purpose_type', 'course_id', 'course_name', 
            'program', 'section', 'topic', 'start_date', 'end_date', 
            'start_time', 'end_time'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(is_active=True)
        # Add classes for styling
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.CheckboxSelectMultiple):
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if not all([start_date, end_date, start_time, end_time]):
            return cleaned_data

        from django.utils import timezone

        now = timezone.localtime(timezone.now())
        today = now.date()
        current_time = now.time()

        # 1. Check if start_date is in the past
        if start_date < today:
            self.add_error('start_date', "ไม่สามารถจองวันที่ผ่านมาแล้วได้")

        # 2. Check if start_time is in the past (only if start_date is today)
        if start_date == today:
            if start_time < current_time:
                self.add_error('start_time', "ไม่สามารถจองเวลาที่ผ่านมาแล้วได้")

        # 3. Check if end_date is before start_date
        if end_date < start_date:
            self.add_error('end_date', "วันที่สิ้นสุดต้องไม่หกกว่าวันที่เริ่มต้น")

        # 4. Check if end_time is before or equal to start_time (if same day)
        # Note: For recurring bookings across multiple days, we check time per day
        if start_time >= end_time:
            self.add_error('end_time', "เวลาสิ้นสุดต้องอยู่หลังจากเวลาเริ่มต้น")

        return cleaned_data
