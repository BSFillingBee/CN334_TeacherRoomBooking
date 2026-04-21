# Room Booking System for Academic Staff (Django)

ระบบจองห้องพักสำหรับอาจารย์และบุคลากร พัฒนาด้วย Django เชื่อมต่อกับ TU REST API

## วิธีการติดตั้งสำหรับนักพัฒนาคนอื่น (How to Setup)

หากคุณ Clone โปรเจคนี้ไปใช้งาน ให้ทำตามขั้นตอนดังนี้ครับ:

### 1. เตรียมระบบ (Prerequisites)
- ติดตั้ง **Python 3.10+**
- ติดตั้ง **Git**

### 2. ติดตั้ง Dependencies
```bash
# Clone โปรเจค
git clone https://github.com/BSFillingBee/CN334_TeacherRoomBooking.git
cd CN334_TeacherRoomBooking

# สร้าง Virtual Environment
python -m venv venv

# Activate Virtual Environment
# สำหรับ Windows:
.\venv\Scripts\activate
# สำหรับ Mac/Linux:
source venv/bin/activate

# ติดตั้งไลบรารีที่จำเป็น
pip install -r requirements.txt
```

### 3. ตั้งค่าสภาพแวดล้อม (Environment Variables)
เนื่องจากเราไม่แชร์ไฟล์ `.env` ขึ้น GitHub คุณต้องสร้างเองโดยก๊อปปีจากตัวอย่าง:
1. สร้างไฟล์ชื่อ `.env` ในโฟลเดอร์หลัก
2. คัดลอกเนื้อหาจากไฟล์ `.env.example` ไปใส่
3. แก้ไขค่าต่างๆ เช่น `SECRET_KEY`, `EMAIL_HOST_USER`, และ `TU_APP_KEY` ให้เป็นของคุณเอง

### 4. ตั้งค่าฐานข้อมูล (Database)
```bash
# สร้างฐานข้อมูล (Migrations)
python manage.py migrate

# สร้างบัญชีผู้ดูแลระบบ (Optional)
python manage.py createsuperuser
```

### 5. รันโปรเจค
```bash
python manage.py runserver
```
เข้าใช้งานได้ที่: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🐳 วิธีการรันด้วย Docker (ทางเลือก)
หากคุณมี Docker ติดตั้งอยู่แล้ว สามารถรันโปรเจคได้ง่ายๆ โดยไม่ต้องตั้งค่า Python ในเครื่อง:

1. เตรียมไฟล์ `.env` ให้เรียบร้อย
2. รันคำสั่ง:
```bash
docker-compose up --build
```
ระบบจะสร้าง Container สำหรับ Django และ PostgreSQL ให้โดยอัตโนมัติ

---

## ✨ ฟีเจอร์ที่พร้อมใช้งานแล้ว
- ✅ **TU Single Sign-On:** เข้าใช้งานด้วยระบบ TU REST API (Ad/verify)
- ✅ **Monthly Calendar:** ปฏิทินแสดงการใช้ห้องแบบรายเดือน พร้อมระบบนำทาง
- ✅ **Conflict Detection:** ระบบป้องกันการจองซ้ำซ้อน 100% (ตรวจสอบทั้งรายการที่มีอยู่และรายการที่รออนุมัติ)
- ✅ **Past Booking Prevention:** ป้องกันการจองวันที่หรือเวลาที่ผ่านมาแล้ว
- ✅ **Section Support:** รองรับการระบุ "กลุ่มเรียน" สำหรับวิชาเรียนปกติ
- ✅ **Admin Workflow:** ระบบจัดการและอนุมัติการจองสำหรับเจ้าหน้าที่
- ✅ **Responsive Design:** หน้าตา UI ทันสมัย รองรับการใช้งานผ่านมือถือ
