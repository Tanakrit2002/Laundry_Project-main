# คู่มือการติดตั้งโปรเจกต์ ระบบจัดการร้านซักรีด (Laundary System)

## ส่วนที่ 1: ติดตั้ง SQL Server 2019

ดาวน์โหลดไฟล์จาก
https://drive.google.com/drive/folders/1irIl3hucADoWOF18coyQ2ZGdMmAnPcH-

ขั้นตอน
เปิดไฟล์ → เลือก Download Media
เลือกประเภท: Express Advanced
เลือกตำแหน่งติดตั้ง
เมื่อโหลดเสร็จ → กด Open folder
ดับเบิลคลิกไฟล์ → กด OK เพื่อแตกไฟล์
การติดตั้ง

เลือก: New SQL Server stand-alone installation
ติ๊ก ✔️ I accept the license terms → Next

ตั้งค่า
Instance Name: SQLExpress2019
Authentication Mode: Mixed Mode
Login :
Username: sa
Password: 123456789
➡️ ติดตั้งจนเสร็จ แล้วกด Close

## 🛠️ ส่วนที่ 2: ติดตั้ง SQL Server Management Studio (SSMS)
ดาวน์โหลดจากลิงก์เดียวกัน
เปิดไฟล์ติดตั้ง
กด Install
รอจนเสร็จ → กด Close

## 🔌 ส่วนที่ 3: ติดตั้ง ODBC Driver 17
ขั้นตอน: Next → Modify → Next → Install → Finish

## 🐍 ส่วนที่ 4: ติดตั้ง Python
🔗 https://www.python.org/downloads/
ขั้นตอน
ดาวน์โหลดเวอร์ชันล่าสุด
เปิดไฟล์ .exe
กด Install
ตรวจสอบ
```Bash
python --version
```
## 📦 ส่วนที่ 5: ตรวจสอบ pip
```Bash
pip --version
```
## 💻 ส่วนที่ 6: ติดตั้งโปรเจกต์
1. ดาวน์โหลดโปรเจกต์
ไปที่ GitHub กด Code → Download ZIP แตกไฟล์ (Extract All...)
2. เปิดโปรเจกต์
เปิด Visual Studio Code ไปที่: File > Open Folder
3. เปิด Terminal
Terminal → New Terminal
4. ติดตั้งไลบรารี
```Bash
pip install django mssql-django django-crispy-forms crispy-bootstrap5 openpyxl
```
ถ้ามีปัญหา:
```Bash
python -m pip install django mssql-django django-crispy-forms crispy-bootstrap5 openpyxl
```
## 🗄️ ส่วนที่ 7: นำเข้าฐานข้อมูล
เปิด SQL Server Management Studio

Login:
Username: sa
Password: 123456789
Restore Database
คลิกขวา Databases
เลือก Restore Database...
เลือก: Device → ... → Add
เลือกไฟล์: LaundryDB.bak
กด OK
✅ จะเห็นฐานข้อมูล LaundryDB

## ⚙️ ส่วนที่ 8: ตั้งค่า Database ใน Django

ไปที่ไฟล์: laundry_project/settings.py

แก้ไข:

```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'LaundryDB',
        'USER': 'sa',
        'PASSWORD': '123456789',
        'HOST': 'DESKTOP-XXXX\\SQLExpress2019',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes;',
        },
    }
}
```

⚠️ หมายเหตุ: \\ ต้องใส่ 2 ตัว, เปลี่ยน HOST ให้ตรงกับเครื่องของคุณ

## 🚀 ส่วนที่ 9: เริ่มใช้งานระบบ
cd laundry_project
python manage.py runserver

👉 กด Ctrl + Click ที่ลิงก์เพื่อเปิดเว็บ

🔐 ข้อมูลเข้าสู่ระบบ
👑 Admin

username: admin

password: 1234

เมื่อล็อกอินสำเร็จ ระบบพร้อมใช้งานทันที 🎉
✅ พร้อมใช้งาน
---









