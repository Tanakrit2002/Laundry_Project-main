from django.contrib import admin
from .models import Role, Employee, Customer, Service, Order, Order_Item, Payment, Process_Tracking

# ปรับแต่งการแสดงผลตารางลูกค้า
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('CUS_ID', 'CUSName', 'CUSPhone', 'CUSLine', 'Created_at')
    search_fields = ('CUSName', 'CUSPhone')

# ปรับแต่งการแสดงผลตารางพนักงาน
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('EMP_ID', 'EMPName', 'Role', 'EMPPhone')
    search_fields = ('EMPName',)

# ปรับแต่งการแสดงผลตารางบริการ
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('Service_ID', 'ServiceType', 'FabricType', 'PriceService')

# ปรับแต่งการแสดงผลตารางออเดอร์
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('Order_ID', 'CUS', 'EMP', 'Status', 'Totalprice', 'Order_Date')
    list_filter = ('Status',)

# ตารางอื่นๆ ลงทะเบียนแบบมาตรฐาน
admin.site.register(Role)
admin.site.register(Order_Item)
admin.site.register(Payment)
admin.site.register(Process_Tracking)