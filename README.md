# คู่มือการติดตั้งโปรเจกต์ ระบบจัดการร้านซักรีด (Laundary System)

## ส่วนที่ 1: ติดตั้ง SQL Server 2019

ดาวน์โหลดไฟล์จาก
https://drive.google.com/drive/folders/1irIl3hucADoWOF18coyQ2ZGdMmAnPcH-

หลังจากดาวน์โหลดแล้วให้เปิดไฟล์และเลือก Download Media จากนั้นเลือกประเภทเป็น Express Advanced และกำหนดตำแหน่งติดตั้ง เมื่อดาวน์โหลดเสร็จให้กด Open folder และดับเบิลคลิกไฟล์ที่ได้ จากนั้นกด OK เพื่อแตกไฟล์

ในขั้นตอนการติดตั้ง ให้เลือก
New SQL Server stand-alone installation or add features to an existing installation

ยอมรับเงื่อนไขโดยติ๊ก I accept the license terms แล้วกด Next ไปเรื่อย ๆ

ในขั้นตอน Feature Selection ให้เอาเครื่องหมายถูกบางตัวออกตามภาพต้นฉบับ (ที่กำหนดไว้)

ตั้งชื่อ Instance เป็น SQLExpress2019

เลือก Authentication Mode เป็น Mixed Mode และตั้งค่า

Username: sa
Password: 123456789

จากนั้นดำเนินการติดตั้งจนเสร็จและกด Close

🔹 ส่วนที่ 2: ติดตั้ง SQL Server Management Studio (SSMS 19)

ดาวน์โหลดจากลิงก์เดียวกัน เปิดไฟล์ติดตั้ง เลือกตำแหน่งที่ต้องการ จากนั้นกด Install และรอจนติดตั้งเสร็จแล้วกด Close

🔹 ส่วนที่ 3: ติดตั้ง ODBC Driver 17

เปิดไฟล์ติดตั้ง จากนั้นกด Next → เลือก Modify → กด Next → กด Install และเมื่อเสร็จแล้วกด Finish

🔹 ส่วนที่ 4: ติดตั้ง Python

เข้าเว็บไซต์ https://www.python.org/downloads/
 และดาวน์โหลด Python เวอร์ชันล่าสุดสำหรับ Windows

หลังจากดาวน์โหลดแล้วให้เปิดไฟล์ .exe และกด Install รอจนติดตั้งเสร็จ

ตรวจสอบการติดตั้งโดยเปิด Command Prompt และพิมพ์

python --version

หรือ

py --version

หากติดตั้งสำเร็จจะปรากฏเวอร์ชัน Python

🔹 ส่วนที่ 5: ตรวจสอบ pip

เปิด Command Prompt แล้วพิมพ์

pip --version

หากมีการแสดงเวอร์ชัน แสดงว่าสามารถใช้งานได้

🔹 ส่วนที่ 6: ติดตั้งโปรเจกต์

เข้าไปที่ GitHub ของโปรเจกต์ กด Code → Download ZIP จากนั้นแตกไฟล์ ZIP โดยคลิกขวาและเลือก Extract All...

เปิดโปรแกรม Visual Studio Code แล้วเลือก File > Open Folder จากนั้นเลือกโฟลเดอร์โปรเจกต์ที่แตกไฟล์ไว้

เปิด Terminal โดยไปที่เมนู Terminal → New Terminal

ติดตั้งไลบรารีด้วยคำสั่ง

pip install django mssql-django django-crispy-forms crispy-bootstrap5 openpyxl

หากมีปัญหาให้ใช้

python -m pip install django mssql-django django-crispy-forms crispy-bootstrap5 openpyxl
🔹 ส่วนที่ 7: นำเข้าฐานข้อมูล

เปิด SQL Server Management Studio และเข้าสู่ระบบด้วย

Username: sa
Password: 123456789

จากนั้นคลิกขวาที่ Databases เลือก Restore Database...

เลือก Device → กด ... → Add → เลือกไฟล์ LaundryDB.bak จากโฟลเดอร์โปรเจกต์ → กด OK

เมื่อเสร็จแล้วจะเห็นฐานข้อมูล LaundryDB

---









