from django.db import models

class Room(models.Model):
    ROOM_TYPES = (
        ('MEETING', 'ห้องประชุม'),
        ('LECTURE', 'ห้องบรรยาย'),
    )
    
    code = models.CharField(max_length=20, unique=True, verbose_name='รหัสห้อง')
    name = models.CharField(max_length=100, verbose_name='ชื่อห้อง')
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, verbose_name='ประเภท')
    capacity = models.IntegerField(verbose_name='จำนวนที่นั่ง')
    is_active = models.BooleanField(default=True, verbose_name='เปิดใช้งาน')
    image = models.CharField(max_length=255, blank=True, null=True, verbose_name='รูปภาพห้อง (URL)')

    class Meta:
        verbose_name = 'ห้อง'
        verbose_name_plural = 'ห้อง'

    def __str__(self):
        return f"{self.code} - {self.name}"


class BlackoutPeriod(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='blackout_periods',
        verbose_name='ห้อง',
        null=True,
        blank=True,
        help_text='ถ้าไม่เลือกห้อง = ปิดทุกห้องพร้อมกัน',
    )
    title = models.CharField(max_length=200, verbose_name='ชื่อช่วงเวลาปิด เช่น ปิดเทอมภาคฤดูร้อน')
    start_date = models.DateField(verbose_name='วันเริ่มต้น')
    end_date = models.DateField(verbose_name='วันสิ้นสุด')
    note = models.TextField(blank=True, null=True, verbose_name='หมายเหตุ')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'ช่วงเวลาปิดห้อง'
        verbose_name_plural = 'ช่วงเวลาปิดห้อง'
        ordering = ['-start_date']

    def __str__(self):
        room_str = self.room.code if self.room else 'ทุกห้อง'
        return f"{self.title} ({room_str}: {self.start_date} – {self.end_date})"
