from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('LECTURER', 'อาจารย์'),
        ('ADMIN', 'เจ้าหน้าที่ (Admin)'),
    )
    
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='LECTURER',
        verbose_name='สิทธิ์การใช้งาน'
    )
    
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name='เบอร์โทรศัพท์'
    )

    class Meta:
        verbose_name = 'ผู้ใช้งาน'
        verbose_name_plural = 'ผู้ใช้งาน'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_lecturer(self):
        return self.role == 'LECTURER'
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN'
