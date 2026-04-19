from django.db import models

class Role(models.Model):
    Role_ID = models.AutoField(primary_key=True)
    RoleName = models.CharField(max_length=50)
    Permissions = models.TextField(null=True, blank=True) # 🚨 ต้องมีอันนี้นะ!
    Description = models.CharField(max_length=255, blank=True, null=True)
    

    def __str__(self):
        return self.RoleName

from django.contrib.auth.models import User  # 🚨 เพิ่มบรรทัดนี้เข้าไป!
class Employee(models.Model):
    EMP_ID = models.AutoField(primary_key=True)
    Role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    EMPName = models.CharField(max_length=100)
    EMPAddress = models.CharField(max_length=255, blank=True, null=True)
    EMPPhone = models.CharField(max_length=10)
    Created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="บัญชีผู้ใช้งาน")

    def __str__(self):
        return self.EMPName

class Customer(models.Model):
    CUS_ID = models.AutoField(primary_key=True)
    CUSName = models.CharField(max_length=100)
    CUSPhone = models.CharField(max_length=10)
    CUSLine = models.CharField(max_length=50, blank=True, null=True)
    CUSAddress = models.CharField(max_length=255, blank=True, null=True)
    Created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.CUSName

class Service(models.Model):
    Service_ID = models.AutoField(primary_key=True)
    ServiceType = models.CharField(max_length=100)
    FabricType = models.CharField(max_length=100)
    PriceService = models.DecimalField(max_digits=10, decimal_places=2)
    Unit = models.CharField(max_length=50, null=True, blank=True, verbose_name="หน่วย")

    def __str__(self):
        return f"{self.ServiceType} - {self.FabricType}"

class Order(models.Model):
    Order_ID = models.AutoField(primary_key=True)
    CUS = models.ForeignKey(Customer, on_delete=models.CASCADE)
    EMP = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    Order_Date = models.DateTimeField(auto_now_add=True)
    Status = models.CharField(max_length=50)
    Totalprice = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.Order_ID}"

class Order_Item(models.Model):
    Item_ID = models.AutoField(primary_key=True)
    Order = models.ForeignKey(Order, on_delete=models.CASCADE)
    Service = models.ForeignKey(Service, on_delete=models.CASCADE)
    Quantity = models.IntegerField(default=1)
    Unit = models.CharField(max_length=50, default='ชิ้น')
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    Item_Status = models.CharField(max_length=50, default='รอดำเนินการ') # เก็บสถานะย่อย เช่น 'กำลังซัก', 'ซักเสร็จสิ้น'

class Payment(models.Model):
    Payment_ID = models.AutoField(primary_key=True)
    Order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    Payment_Date = models.DateTimeField(auto_now_add=True)
    Payment_Method = models.CharField(max_length=50)
    Payment_Status = models.CharField(max_length=50)

class Process_Tracking(models.Model):
    Process_ID = models.AutoField(primary_key=True)
    Order = models.ForeignKey(Order, on_delete=models.CASCADE)
    EMP = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    Step = models.CharField(max_length=255)
    Status = models.CharField(max_length=50)
    Updated_at = models.DateTimeField(auto_now=True)