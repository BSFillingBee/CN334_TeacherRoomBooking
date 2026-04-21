from django.db import models
from django.conf import settings
from rooms.models import Room

class Booking(models.Model):
    PURPOSE_TYPES = (
        ('TEACHING', 'สอนปกติ/ชดเชย/เสริม'),
        ('TRAINING', 'จัดอบรม/จัดติว'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'รอการอนุมัติ'),
        ('APPROVED', 'อนุมัติแล้ว'),
        ('REJECTED', 'ปฏิเสธ'),
        ('CANCELLED', 'ยกเลิกโดยผู้จอง'),
    )
    
    PROGRAM_CHOICES = (
        ('NORMAL', 'ปริญญาตรีภาคปกติ'),
        ('MASTER', 'ปริญญาโท'),
        ('TEP_TEPE', 'TEP-TEPE'),
        ('TU_PINE', 'TU-PINE'),
    )

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name='ผู้จอง'
    )
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        verbose_name='ห้องที่เลือก'
    )
    
    purpose_type = models.CharField(
        max_length=10, 
        choices=PURPOSE_TYPES, 
        verbose_name='วัตถุประสงค์'
    )
    
    # Fields for Teaching
    course_id = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name='รหัสวิชา'
    )
    course_name = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name='ชื่อวิชา'
    )
    program = models.CharField(
        max_length=20, 
        choices=PROGRAM_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name='หลักสูตร'
    )
    
    # Fields for Training
    topic = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name='ชื่อเรื่อง/หัวข้ออบรม'
    )

    # Date and Time
    start_date = models.DateField(verbose_name='วันที่เริ่มต้น')
    end_date = models.DateField(verbose_name='วันที่สิ้นสุด')
    
    # Recurring days (Comma separated values: 0=Mon, 1=Tue, ..., 4=Fri)
    # FR-BOOK-04: Mon-Fri
    days_of_week = models.CharField(
        max_length=50, 
        help_text='เก็บเป็นตัวเลข 0-4 คั่นด้วยเครื่องหมายจุลภาค',
        verbose_name='วันที่ใช้งานในสัปดาห์'
    )
    
    start_time = models.TimeField(verbose_name='เวลาเริ่มต้น')
    end_time = models.TimeField(verbose_name='เวลาสิ้นสุด')

    # Approval Status
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='PENDING',
        verbose_name='สถานะการจอง'
    )
    rejection_reason = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='เหตุผลในกรณีปฏิเสธ'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='สร้างเมื่อ')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='แก้ไขล่าสุด')

    class Meta:
        verbose_name = 'การจอง'
        verbose_name_plural = 'การจอง'
        ordering = ['-created_at']

    def __str__(self):
        purpose = self.course_name if self.purpose_type == 'TEACHING' else self.topic
        return f"{self.room.code} - {purpose} ({self.requester.username})"
    
    def get_days_list(self):
        return [d.strip() for d in self.days_of_week.split(',') if d.strip()]
