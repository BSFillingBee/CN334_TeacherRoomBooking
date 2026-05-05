# ระบบจองห้องประชุม — ภาควิชาวิศวกรรมไฟฟ้าและคอมพิวเตอร์

Django Web Application สำหรับจองห้องประชุม/ห้องเรียนภายในภาควิชา  
รองรับการยืนยันตัวตนผ่าน TU REST API, ระบบอนุมัติ, ปฏิทิน, และรายงานสถิติ

---

## Requirements

- Python 3.10–3.12 (แนะนำ 3.12)

```
pip install -r requirements.txt
```

---

## ติดตั้งและรันระบบ

```bash
# 1. สร้าง virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 2. ติดตั้ง dependencies
pip install -r requirements.txt
# ถ้าไม่ได้ pip install Django==5.2 requests==2.32.3 whitenoise==6.9.0 python-dotenv==1.1.0 gunicorn==23.0.0


# 3. สร้างฐานข้อมูล + ใส่ข้อมูลห้อง 5 ห้องเริ่มต้น
python manage.py migrate

#superuser หรือ รันตั้งค่าadmin
python manage.py createsuperuser

### ตั้งค่า Admin (ทำครั้งแรกครั้งเดียว)
```bash
python manage.py shell -c "
from accounts.models import User
u, _ = User.objects.get_or_create(username='admin')
u.role = 'ADMIN'
u.set_unusable_password()
u.save()
print('Admin ready — login with username=admin password=tu1234')
"
```


# 4. รันเซิร์ฟเวอร์
python manage.py runserver
```

เปิด browser ที่ `http://localhost:8000/login/`

> หมายเหตุ: `http://localhost:8000/` จะ redirect ไปหน้า Login อัตโนมัติ  
> ถ้า login แล้วจะ redirect ไป Dashboard หรือ Admin panel ตาม Role

---

## การเข้าสู่ระบบ (Mock Mode)

ค่าเริ่มต้นใช้ Mock API (ไม่ต้องเชื่อม TU REST API จริง)

| Username | Password | หมายเหตุ |
|---|---|---|
| ชื่อใดก็ได้ | `tu1234` | ได้ Role Lecturer |

---

## ตั้งค่า .env (optional)

สร้างไฟล์ `.env` ที่ root:

```env
MOCK_API=True
TU_APP_KEY=your_key_from_restapi.tu.ac.th
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
BASE_URL=http://localhost:8000
```

เปลี่ยน `MOCK_API=False` เมื่อพร้อมใช้ TU REST API จริง

---

## ห้องในระบบ (ตาม SRS)

| รหัส | ชื่อ | ประเภท | ที่นั่ง |
|---|---|---|---|
| 406-3 | ห้องประชุม 1 | ห้องประชุม | 60 |
| 406-5 | ห้องประชุม 2 | ห้องประชุม | 15 |
| 408-1 | ห้องประชุม 3 | ห้องประชุม | 10 |
| 408-2/1 | ห้องบรรยาย 1 | ห้องเรียน | 20 |
| 408-2/2 | ห้องบรรยาย 2 | ห้องเรียน | 20 |

---

## URL หลัก

| Path | หน้า | สิทธิ์ |
|---|---|---|
| `/login/` | หน้า Login | ทุกคน |
| `/dashboard/` | Dashboard | Lecturer |
| `/calendar/` | ปฏิทิน (รายเดือน/สัปดาห์) | ทุกคน |
| `/rooms/` | รายการห้อง | ทุกคน |
| `/map/` | แผนผังชั้น 4 | ทุกคน |
| `/bookings/new/` | จองห้อง | Lecturer |
| `/bookings/my/` | การจองของฉัน | Lecturer |
| `/ai-booking/` | จองด้วย AI | Lecturer |
| `/admin-panel/` | อนุมัติการจอง | Admin |
| `/admin-panel/rooms/` | จัดการห้อง | Admin |
| `/admin-panel/reports/` | รายงานสถิติ + Export CSV | Admin |
| `/admin-panel/users/` | จัดการ Role ผู้ใช้ | Admin |
| `/admin/` | Django Admin | Superuser |
