import json
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Order, Order_Item, Process_Tracking, Customer, Service, Employee, Payment, Role
from .forms import CustomerForm
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.db import DatabaseError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def get_current_employee(user):
    if user.is_authenticated:
        try:
            return Employee.objects.get(user=user)
        except Employee.DoesNotExist:
            return None
    return None


@login_required
def dashboard(request):
    s_id = request.GET.get('search_id', '').strip()
    s_name = request.GET.get('search_name', '').strip()
    s_pay = request.GET.get('search_pay', '').strip()
    s_status = request.GET.get('search_status', '').strip()
    s_date = request.GET.get('search_date', '').strip()

    # 1. นับจำนวนเฉพาะงานที่ยังค้างอยู่ในระบบ (ไม่รวมที่ปิดงานแล้ว)
    pending_count = Order.objects.filter(Status='รอชำระเงิน').count()
    processing_count = Order.objects.filter(Status__in=['รอดำเนินการ', 'กำลังดำเนินการ']).count()
    # นับเฉพาะงานที่ซักเสร็จแล้วแต่ลูกค้ายอมรับผ้า (ถ้าปิดงานแล้วจะไม่นับ)
    done_count = Order.objects.filter(Status='งานเสร็จสิ้น').count()

    today = timezone.now().date()
    today_revenue = Payment.objects.filter(Payment_Date__date=today).aggregate(total=Sum('amount'))['total'] or 0

    where_clauses = ["1=1"]
    params = []

    if s_id:
        clean_id = s_id.upper().replace('LD-', '').lstrip('0')
        if clean_id.isdigit():
            where_clauses.append("o.Order_ID = %s")
            params.append(clean_id)

    if s_name:
        where_clauses.append("c.CUSName LIKE %s")
        params.append(f"%{s_name}%")

    if s_pay == 'ชำระเงินแล้ว':
        where_clauses.append("p.Payment_ID IS NOT NULL")
    elif s_pay == 'รอชำระเงิน':
        where_clauses.append("p.Payment_ID IS NULL")

    # 2. ปรับการ Filter ให้ตรงกับ Dropdown ในหน้า Dashboard
    if s_status:
        if s_status == 'รอพนักงานรับงาน':
            where_clauses.append("o.Status = N'ชำระเงินแล้ว'")
        elif s_status == 'ซักเสร็จสิ้น / รอรับคืน':
            where_clauses.append("o.Status = N'งานเสร็จสิ้น'")
        elif s_status == 'งานเสร็จสิ้น/ติดต่อรับผ้า':
            where_clauses.append("o.Status = N'งานเสร็จสิ้น'")
        elif s_status == 'ปิดงานแล้ว':
            where_clauses.append("o.Status IN (N'ลูกค้ารับผ้าเรียบร้อย', N'ปิดงาน')")
        else:
            where_clauses.append("o.Status = %s")
            params.append(s_status)

    if s_date:
        where_clauses.append("CAST(o.Order_Date AS DATE) = %s")
        params.append(s_date)

    query = f"""
        SELECT
            dbo.fn_FormatBillID(o.Order_ID) AS DisplayOrderID,
            o.Order_ID,
            c.CUSName,
            o.Status,
            o.Totalprice,
            o.Order_Date,
            CASE
                WHEN p.Payment_ID IS NULL THEN N'รอชำระเงิน'
                ELSE N'ชำระเงินแล้ว'
            END AS PaymentStatus
        FROM core_order o
        JOIN core_customer c ON o.CUS_id = c.CUS_ID
        LEFT JOIN core_payment p ON p.Order_id = o.Order_ID
        WHERE {" AND ".join(where_clauses)}
        ORDER BY o.Order_Date DESC
    """

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        orders_raw = [dict(zip(columns, row)) for row in cursor.fetchall()[:10]]

    # 3. ดึงสถานะปัจจุบันมาแสดงในตารางโดยตรง ไม่ต้อง Loop เช็คไอเทมซ้ำซ้อน
    for o in orders_raw:
        o['slowest_status'] = o['Status']

    # ข้อมูลกราฟ (คงเดิม)
    seven_days_ago = today - timedelta(days=6)
    orders_last_7_days = Order.objects.filter(Order_Date__date__gte=seven_days_ago)
    weekly_dict = {(today - timedelta(days=i)).strftime('%d/%m'): 0 for i in range(6, -1, -1)}
    for og in orders_last_7_days:
        ds = og.Order_Date.strftime('%d/%m')
        if ds in weekly_dict:
            weekly_dict[ds] += 1

    top_services = Order_Item.objects.values('Service__ServiceType').annotate(total_count=Count('Service')).order_by('-total_count')[:4]

    context = {
        'orders': orders_raw,
        'pending_count': pending_count,
        'processing_count': processing_count,
        'done_count': done_count,
        'today_revenue': today_revenue,
        'labels_weekly': json.dumps(list(weekly_dict.keys()), ensure_ascii=False),
        'data_weekly': json.dumps(list(weekly_dict.values())),
        'labels_services': json.dumps([s['Service__ServiceType'] for s in top_services], ensure_ascii=False),
        'data_services': json.dumps([s['total_count'] for s in top_services]),
        'current_employee': get_current_employee(request.user),
    }
    return render(request, 'dashboard.html', context)


@login_required
def add_order(request):
    current_emp = get_current_employee(request.user) or Employee.objects.first()

    s_id = request.GET.get('search_id', '').strip()
    s_name = request.GET.get('search_name', '').strip()
    s_status = request.GET.get('search_status', '').strip()
    s_date = request.GET.get('search_date', '').strip()
    page = request.GET.get('page', 1)

    orders_qs = Order.objects.all()

    if s_id:
        clean_id = s_id.upper().replace('LD-', '').lstrip('0')
        if clean_id.isdigit():
            orders_qs = orders_qs.filter(Order_ID=clean_id)

    if s_name:
        orders_qs = orders_qs.filter(CUS__CUSName__icontains=s_name)

    if s_date:
        orders_qs = orders_qs.filter(Order_Date__date=s_date)

    if s_status:
        if s_status == 'ชำระเงินแล้ว':
            orders_qs = orders_qs.filter(payment__isnull=False).distinct()
        elif s_status == 'รอชำระเงิน':
            orders_qs = orders_qs.filter(payment__isnull=True).distinct()

    orders_qs = orders_qs.order_by('-Order_Date')
    paginator = Paginator(orders_qs, 10)

    try:
        recent_orders = paginator.page(page)
    except PageNotAnInteger:
        recent_orders = paginator.page(1)
    except EmptyPage:
        recent_orders = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        if customer_id:
            customer = Customer.objects.get(CUS_ID=customer_id)
        else:
            customer = Customer.objects.create(
                CUSName=request.POST.get('new_cus_name'),
                CUSPhone=request.POST.get('new_cus_phone'),
                CUSLine=request.POST.get('new_cus_line'),
                CUSAddress=request.POST.get('new_cus_address')
            )

        items = json.loads(request.POST.get('cart_data')) if request.POST.get('cart_data') else []
        total_price = sum(float(item['price']) * float(item['qty']) for item in items)

        order = Order.objects.create(
            CUS=customer,
            EMP=current_emp,
            Status='รอชำระเงิน',
            Totalprice=total_price
        )

        for item in items:
            service = Service.objects.get(Service_ID=item['service_id'])
            Order_Item.objects.create(
                Order=order,
                Service=service,
                Quantity=item['qty'],
                Unit=item['unit'],
                Price=item['price'],
                Item_Status='รอชำระเงิน'
            )

        Process_Tracking.objects.create(Order=order, EMP=current_emp, Step='เปิดบิล', Status='รอชำระเงิน')

        with connection.cursor() as cursor:
            cursor.execute(
                "EXEC dbo.sp_UpdateOrderStatus %s, %s, %s",
                [order.Order_ID, 'รอชำระเงิน', current_emp.EMP_ID]
            )

        return redirect('add_order')

    return render(request, 'add_order.html', {
        'customers': Customer.objects.all(),
        'services': Service.objects.all(),
        'recent_orders': recent_orders,
        'current_employee': current_emp,
    })


@login_required
def manage_orders(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_OrderSummary WHERE Status = N'ชำระเงินแล้ว' ORDER BY Order_Date ASC")
        orders = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    return render(request, 'manage_orders.html', {
        'orders': orders,
        'employees': Employee.objects.all(),
        'current_employee': get_current_employee(request.user)
    })


@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        order = Order.objects.get(Order_ID=order_id)
        payment_method = request.POST.get('payment_method')
        current_emp = get_current_employee(request.user) or Employee.objects.first()

        if payment_method:
            Payment.objects.get_or_create(
                Order=order,
                defaults={
                    'amount': order.Totalprice,
                    'Payment_Method': payment_method,
                    'Payment_Status': 'ชำระเงินเรียบร้อย'
                }
            )

            Order_Item.objects.filter(
                Order=order,
                Item_Status='รอชำระเงิน'
            ).update(Item_Status='ชำระเงินแล้ว')

            if not new_status:
                new_status = 'ชำระเงินแล้ว'

        if new_status:
            Process_Tracking.objects.create(
                Order=order,
                EMP=current_emp,
                Step=f'อัปเดตสถานะเป็น: {new_status}',
                Status=new_status
            )

            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC dbo.sp_UpdateOrderStatus %s, %s, %s",
                    [order_id, new_status, current_emp.EMP_ID]
                )

        next_url = request.POST.get('next')
        if next_url == 'add_order':
            return redirect('add_order')

        if next_url == 'contact_customer_list':
            return redirect('contact_customer_list')

        if new_status == 'งานเสร็จสิ้น':
            return redirect('laundry_queue')

        if new_status in ['ลูกค้ารับผ้าเรียบร้อย', 'ปิดงาน']:
            return redirect('contact_customer_list')

        return redirect('dashboard')

    return redirect('dashboard')

@login_required
def assign_task(request, order_id):
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        if not emp_id:
            messages.error(request, 'กรุณาเลือกพนักงาน')
            return redirect('manage_orders')

        assigned_emp = Employee.objects.get(EMP_ID=emp_id)
        current_emp = get_current_employee(request.user) or Employee.objects.first()
        order = Order.objects.get(Order_ID=order_id)

        # ถ้าหน้า queue ต้องโชว์ "ผู้รับผิดชอบ" เป็นสมปอง
        # ต้องเขียนลง order.EMP ตรงนี้เลย
        order.EMP = assigned_emp
        order.Status = 'รอดำเนินการ'
        order.save(update_fields=['EMP', 'Status'])

        Order_Item.objects.filter(Order=order).update(Item_Status='รอดำเนินการ')

        Process_Tracking.objects.create(
            Order=order,
            EMP=current_emp,
            Step=f'มอบหมายงานให้: {assigned_emp.EMPName}',
            Status='รอดำเนินการ'
        )

        with connection.cursor() as cursor:
            cursor.execute(
                "EXEC dbo.sp_UpdateOrderStatus %s, %s, %s",
                [order_id, 'รอดำเนินการ', assigned_emp.EMP_ID]
            )

    return redirect('manage_orders')

@login_required
def laundry_queue(request):
    current_emp = get_current_employee(request.user)

    query = """
        SELECT
            dbo.fn_FormatBillID(o.Order_ID) AS DisplayOrderID,
            o.Order_ID,
            c.CUSName,
            c.CUSPhone,
            e.EMPName,
            o.Order_Date,
            o.Status
        FROM core_order o
        JOIN core_customer c ON o.CUS_id = c.CUS_ID
        JOIN core_employee e ON o.EMP_id = e.EMP_ID
        WHERE o.Status IN (N'รอดำเนินการ', N'กำลังดำเนินการ')
    """
    params = []

    if not request.user.is_superuser and (current_emp and current_emp.Role.RoleName != 'Admin'):
        query += " AND o.EMP_id = %s"
        params.append(current_emp.EMP_ID)

    query += " ORDER BY o.Order_Date ASC"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        tasks_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for row in tasks_data:
            row['items'] = Order_Item.objects.filter(Order_id=row['Order_ID'])

    return render(request, 'laundry_queue.html', {
        'tasks': tasks_data,
        'employees': Employee.objects.all(),
        'current_employee': current_emp
    })


@login_required
def update_item_process(request, order_id):
    if request.method == 'POST':
        try:
            new_status = request.POST.get('new_status')
            order = Order.objects.get(Order_ID=order_id)
            current_emp = get_current_employee(request.user) or Employee.objects.first()

            if not new_status:
                return redirect('laundry_queue')

            allowed_statuses = ['รอดำเนินการ', 'กำลังดำเนินการ', 'งานเสร็จสิ้น']
            if new_status not in allowed_statuses:
                return redirect('laundry_queue')

            current_status = order.Status

            next_allowed = {
                'รอดำเนินการ': ['กำลังดำเนินการ'],
                'กำลังดำเนินการ': ['งานเสร็จสิ้น'],
                'งานเสร็จสิ้น': [],
            }

            if current_status in next_allowed:
                if new_status != current_status and new_status not in next_allowed[current_status]:
                    return redirect('/laundry-queue/?error=skip')
            else:
                return redirect('/laundry-queue/?error=skip')

            Order_Item.objects.filter(Order=order).update(Item_Status=new_status)

            service_names = []
            for oi in order.order_item_set.select_related('Service').all():
                service_label = oi.Service.ServiceType
                if service_label not in service_names:
                    service_names.append(service_label)

            services_text = ", ".join(service_names)

            Process_Tracking.objects.create(
                Order=order,
                EMP=current_emp,
                Step=f"อัปเดตผ้าทั้งออเดอร์: {services_text} เป็น {new_status}",
                Status=new_status
            )

            order.Status = new_status
            order.save(update_fields=['Status'])

            # สำคัญ: ส่ง EMP เดิมของ order เข้า procedure
            # เพื่อคงผู้รับผิดชอบงานในคิวไว้ ไม่ใช่เอาคนกดล่าสุดไปทับ
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC dbo.sp_UpdateOrderStatus %s, %s, %s",
                    [order.Order_ID, new_status, order.EMP_id]
                )

            return redirect('laundry_queue')

        except DatabaseError:
            return redirect('/laundry-queue/?error=skip')

    return redirect('laundry_queue')


@login_required
def contact_customer_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_PickupList ORDER BY Order_Date DESC")
        columns = [col[0] for col in cursor.description]
        orders_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return render(request, 'contact_customer.html', {
        'orders': orders_data,
        'current_employee': get_current_employee(request.user)
    })


@login_required
def system_settings(request):
    if request.method == 'POST':
        if 'add_service' in request.POST:
            Service.objects.create(
                ServiceType=request.POST.get('service_type'),
                FabricType=request.POST.get('fabric_type'),
                PriceService=request.POST.get('price'),
                Unit=request.POST.get('unit')
            )
        elif 'update_service' in request.POST:
            service = Service.objects.get(Service_ID=request.POST.get('service_id'))
            service.ServiceType = request.POST.get('service_type')
            service.FabricType = request.POST.get('fabric_type')
            service.PriceService = request.POST.get('price')
            service.Unit = request.POST.get('unit')
            service.save()
        elif 'delete_service' in request.POST:
            Service.objects.filter(Service_ID=request.POST.get('service_id')).delete()
        return redirect('system_settings')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_ServicePriceList ORDER BY ServiceType, FabricType")
        services_data = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    return render(request, 'system_settings.html', {
        'services': services_data,
        'current_employee': get_current_employee(request.user)
    })


@login_required
def customer_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_CustomerContact ORDER BY CUS_ID DESC")
        customers = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    return render(request, 'customer_list.html', {
        'customers': customers,
        'current_employee': get_current_employee(request.user)
    })


@login_required
def completed_orders_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_CompletedHistory ORDER BY CompletedDate DESC")
        orders_data = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    # ==== เพิ่ม 4 บรรทัดนี้ ก่อนบรรทัด return ====
    for order in orders_data:
        items = Order_Item.objects.filter(Order_id=order['Order_ID'])
        details = [f"{i.Service.ServiceType} {i.Service.FabricType}:{i.Quantity}:{i.Price}" for i in items]
        order['ItemDetailsStr'] = "|".join(details)
    # ======================================

    return render(request, 'completed_orders.html', {'orders': orders_data, 'current_employee': get_current_employee(request.user)})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, Order_ID=order_id)
    back_url = request.GET.get('next') or request.META.get('HTTP_REFERER')

    opening_track = Process_Tracking.objects.filter(
        Order=order,
        Step='เปิดบิล'
    ).select_related('EMP').order_by('Process_ID').first()

    opened_by_emp = opening_track.EMP if opening_track and opening_track.EMP else order.EMP

    return render(request, 'order_detail.html', {
        'order': order,
        'items': Order_Item.objects.filter(Order=order),
        'trackings': Process_Tracking.objects.filter(Order=order).order_by('-Process_ID'),
        'current_employee': get_current_employee(request.user),
        'back_url': back_url,
        'opened_by_emp': opened_by_emp,
    })


@login_required
def print_receipt(request, order_id):
    order = get_object_or_404(Order, Order_ID=order_id)
    return render(request, 'print_receipt.html', {
        'order': order,
        'items': Order_Item.objects.filter(Order=order),
        'current_employee': get_current_employee(request.user)
    })


@login_required
def edit_order(request, order_id):
    order = get_object_or_404(Order, Order_ID=order_id)
    current_emp = get_current_employee(request.user) or Employee.objects.first()

    # ดึง "คนเปิดบิล" จาก Timeline
    opening_track = Process_Tracking.objects.filter(
        Order=order,
        Step='เปิดบิล'
    ).select_related('EMP').order_by('Process_ID').first()

    opened_by_emp = opening_track.EMP if opening_track else order.EMP

    if request.method == 'POST':
        items = json.loads(request.POST.get('cart_data')) if request.POST.get('cart_data') else []
        if items:
            order.Totalprice = sum(float(item['price']) * float(item['qty']) for item in items)
            order.save()
            Order_Item.objects.filter(Order=order).delete()

            for item in items:
                service = Service.objects.get(Service_ID=item['service_id'])
                Order_Item.objects.create(
                    Order=order,
                    Service=service,
                    Quantity=item['qty'],
                    Unit=item['unit'],
                    Price=item['price'],
                    Item_Status='รอชำระเงิน'
                )

            Process_Tracking.objects.create(
                Order=order,
                EMP=current_emp,
                Step='อัปเดตรายการผ้า',
                Status=order.Status
            )

            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC dbo.sp_UpdateOrderStatus %s, %s, %s",
                    [order_id, order.Status, current_emp.EMP_ID]
                )
            return redirect('add_order')

    old_items = Order_Item.objects.filter(Order=order)
    cart_list = [{
        'service_id': str(oi.Service.Service_ID),
        'name': f"{oi.Service.ServiceType} - {oi.Service.FabricType}",
        'price': float(oi.Price),
        'qty': oi.Quantity,
        'unit': oi.Unit
    } for oi in old_items]

    return render(request, 'edit_order.html', {
        'order': order,
        'opened_by_emp': opened_by_emp,
        'customers': Customer.objects.all(),
        'services': Service.objects.all(),
        'initial_cart_json': json.dumps(cart_list),
        'current_employee': current_emp
    })

@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, Order_ID=order_id)
    cus = order.CUS
    order.delete()
    if Order.objects.filter(CUS=cus).count() == 0:
        cus.delete()
    return redirect('add_order')


@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CustomerForm()

    return render(request, 'add_customer.html', {
        'form': form,
        'current_employee': get_current_employee(request.user)
    })


@login_required
@transaction.atomic
def manage_users(request):
    if request.method == 'POST':

        if 'add_user' in request.POST:
            first_name = request.POST.get('first_name')
            username = request.POST.get('username')
            password = request.POST.get('password')
            role_name = request.POST.get('role')

            try:
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username นี้มีในระบบแล้ว')
                    return redirect('manage_users')

                new_user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name
                )

                role_obj = Role.objects.filter(RoleName=role_name).first()

                Employee.objects.create(
                    user=new_user,
                    EMPName=first_name,
                    Role=role_obj,
                    EMPPhone="-"
                )

                messages.success(request, 'เพิ่มผู้ใช้งานสำเร็จ')
            except Exception as e:
                messages.error(request, f'เกิดข้อผิดพลาดในการเพิ่มข้อมูล: {str(e)}')

            return redirect('manage_users')

        elif 'edit_user' in request.POST:
            emp_id = request.POST.get('emp_id')
            first_name = request.POST.get('first_name')
            role_name = request.POST.get('role')
            password = request.POST.get('password')

            try:
                emp = Employee.objects.get(pk=emp_id)
                user_obj = emp.user

                if user_obj:
                    user_obj.first_name = first_name
                    if password:
                        user_obj.set_password(password)
                    user_obj.save()

                role_obj = Role.objects.filter(RoleName=role_name).first()
                emp.EMPName = first_name
                emp.Role = role_obj
                emp.save()

                messages.success(request, 'แก้ไขข้อมูลสำเร็จ')
            except Exception as e:
                messages.error(request, f'เกิดข้อผิดพลาดในการแก้ไขข้อมูล: {str(e)}')

            return redirect('manage_users')

        elif 'delete_user' in request.POST:
            emp_id = request.POST.get('emp_id')
            try:
                emp = Employee.objects.get(pk=emp_id)
                user_obj = emp.user

                emp.delete()
                if user_obj:
                    user_obj.delete()

                messages.success(request, 'ลบผู้ใช้งานออกจากระบบเรียบร้อย')
            except Exception as e:
                messages.error(request, f'เกิดข้อผิดพลาดในการลบข้อมูล: {str(e)}')

            return redirect('manage_users')

        elif 'update_permissions' in request.POST:
            role_id = request.POST.get('role_id')
            selected_menus = request.POST.getlist('permissions')
            try:
                role = Role.objects.get(pk=role_id)
                role.Permissions = ",".join(selected_menus)
                role.save()
                messages.success(request, f'อัปเดตสิทธิ์กลุ่ม {role.RoleName} เรียบร้อยแล้ว')
            except Exception as e:
                messages.error(request, f'เกิดข้อผิดพลาดในการอัปเดตสิทธิ์: {str(e)}')
            return redirect('manage_users')

    employees = Employee.objects.select_related('user', 'Role').all()
    roles = Role.objects.all()
    return render(request, 'manage_users.html', {
        'employees': employees,
        'roles': roles,
        'current_employee': get_current_employee(request.user)
    })
