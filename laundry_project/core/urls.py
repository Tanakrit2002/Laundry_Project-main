from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login_root'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('add-order/', views.add_order, name='add_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('edit-order/<int:order_id>/', views.edit_order, name='edit_order'),
    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('print-receipt/<int:order_id>/', views.print_receipt, name='print_receipt'),

    path('add-customer/', views.add_customer, name='add_customer'),
    path('customers/', views.customer_list, name='customer_list'),

    path('manage-orders/', views.manage_orders, name='manage_orders'),
    path('assign-task/<int:order_id>/', views.assign_task, name='assign_task'),
    path('laundry-queue/', views.laundry_queue, name='laundry_queue'),
    path('update-item-process/<int:order_id>/', views.update_item_process, name='update_item_process'),

    path('contact-customer/', views.contact_customer_list, name='contact_customer_list'),
    path('completed-orders/', views.completed_orders_list, name='completed_orders_list'),
    path('system-settings/', views.system_settings, name='system_settings'),

    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('manage-users/', views.manage_users, name='manage_users'),
]