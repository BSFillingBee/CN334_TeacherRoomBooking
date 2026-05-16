import os
import sys
import django
import schedule
import time
import logging
from datetime import datetime

# Setup Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'room_booking.settings')
django.setup()

# Logging (fix UTF-8 สำหรับ Windows)
stream_handler = logging.StreamHandler(
    open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)
)
file_handler = logging.FileHandler('reminder_scheduler.log', encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[stream_handler, file_handler]
)
log = logging.getLogger(__name__)

def send_reminders():
    log.info("กำลังส่ง email เตือน...")
    try:
        from bookings.utils import send_reminder_emails
        sent = send_reminder_emails()
        log.info(f"ส่ง email เตือนสำเร็จ {sent} รายการ")
    except Exception as e:
        log.error(f"เกิดข้อผิดพลาด: {e}")

schedule.every().day.at("08:00").do(send_reminders)

log.info("Reminder Scheduler เริ่มทำงานแล้ว - จะส่ง email ทุกวัน 08:00")
log.info(f"เวลาปัจจุบัน: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log.info("กด Ctrl+C เพื่อหยุด")

while True:
    schedule.run_pending()
    time.sleep(30)