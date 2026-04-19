from django import forms
from .models import Customer, Order

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        # เลือกฟิลด์ที่ต้องการให้กรอก (ไม่ต้องเอา CUS_ID กับ Created_at มา เพราะระบบจัดการให้เอง)
        fields = ['CUSName', 'CUSPhone', 'CUSLine', 'CUSAddress']
        labels = {
            'CUSName': 'ชื่อ-นามสกุลลูกค้า',
            'CUSPhone': 'เบอร์โทรศัพท์',
            'CUSLine': 'LINE ID',
            'CUSAddress': 'ที่อยู่',
        }
        widgets = {
            'CUSName': forms.TextInput(attrs={'class': 'form-control'}),
            'CUSPhone': forms.TextInput(attrs={'class': 'form-control'}),
            'CUSLine': forms.TextInput(attrs={'class': 'form-control'}),
            'CUSAddress': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

        from .models import Order # อย่าลืม import Order ไว้ด้านบนสุดด้วยนะครับ

# สร้างตัวเลือกสถานะ (Dropdown) ให้เลือกง่ายๆ
STATUS_CHOICES = [
    ('Pending', 'รอคิวซัก'),
    ('Doing', 'กำลังดำเนินการ'),
    ('Done', 'ซักเสร็จสิ้น'),
]

class OrderForm(forms.ModelForm):
    # ปรับช่อง Status ให้เป็นแบบ Dropdown เลือกสถานะได้
    Status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label='สถานะเริ่มต้น')

    class Meta:
        model = Order
        # เลือกเฉพาะฟิลด์ที่ต้องกรอกตอนเปิดบิล
        fields = ['CUS', 'EMP', 'Status', 'Note']
        labels = {
            'CUS': 'เลือกลูกค้า',
            'EMP': 'พนักงานรับเรื่อง',
            'Note': 'หมายเหตุ / คำสั่งพิเศษ',
        }
        widgets = {
            'CUS': forms.Select(attrs={'class': 'form-select'}),
            'EMP': forms.Select(attrs={'class': 'form-select'}),
            'Note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'เช่น ระวังเสื้อสีตก, ห้ามรีดไฟแรง'}),
        }