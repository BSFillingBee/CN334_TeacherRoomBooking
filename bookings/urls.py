from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.booking_create, name='booking_create'),
    path('my/', views.booking_list, name='booking_list'),
    path('cancel/<int:pk>/', views.booking_cancel, name='booking_cancel'),
    # Admin routes
    path('admin/approvals/', views.admin_approval_list, name='admin_approval_list'),
    path('admin/approve/<int:pk>/', views.admin_approve_reject, name='admin_approve_reject'),
]
