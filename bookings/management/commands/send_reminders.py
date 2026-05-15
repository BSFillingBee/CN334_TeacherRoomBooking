from django.core.management.base import BaseCommand
from bookings.utils import send_reminder_emails

class Command(BaseCommand):
    help = 'ส่ง Email เตือนผู้จองล่วงหน้า 1 วัน (ควร run ทุกวันตอนเช้าผ่าน cron)'

    def handle(self, *args, **options):
        sent = send_reminder_emails()
        self.stdout.write(self.style.SUCCESS(f'ส่ง Email เตือนสำเร็จ {sent} รายการ'))
