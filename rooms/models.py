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
    image = models.ImageField(upload_to='rooms/', blank=True, null=True, verbose_name='รูปภาพห้อง')

    class Meta:
        verbose_name = 'ห้อง'
        verbose_name_plural = 'ห้อง'

    def __str__(self):
        return f"{self.code} - {self.name}"
