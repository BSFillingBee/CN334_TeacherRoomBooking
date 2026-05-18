from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import template_views as v

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('', v.login_view, name='login'),
    path('login/', v.login_view, name='login'),
    path('logout/', v.logout_view, name='logout'),

    # Staff
    path('dashboard/', v.dashboard, name='dashboard'),
    path('calendar/', v.calendar_view, name='calendar_view'),
    path('rooms/', v.room_list, name='room_list'),
    path('rooms/<int:pk>/', v.room_detail, name='room_detail'),
    path('map/', v.floor_map, name='floor_map'),
    path('bookings/new/', v.book_room, name='book_room'),
    path('bookings/my/', v.my_bookings, name='my_bookings'),
    path('bookings/<int:pk>/cancel/', v.cancel_booking, name='cancel_booking'),
    path('ai-booking/', v.ai_booking, name='ai_booking'),
    path('ai-booking/confirm/', v.ai_confirm_booking, name='ai_confirm_booking'),

    # Admin
    path('admin-panel/', v.admin_approval, name='admin_approval'),
    path('admin-panel/bookings/<int:pk>/review/', v.review_booking, name='review_booking'),
    path('admin-panel/rooms/', v.admin_rooms, name='admin_rooms'),
    path('admin-panel/rooms/add/', v.add_room, name='add_room'),
    path('admin-panel/rooms/<int:pk>/toggle/', v.toggle_room, name='toggle_room'),
    path('admin-panel/rooms/<int:pk>/edit/', v.edit_room, name='edit_room'),
    path('admin-panel/rooms/<int:pk>/delete/', v.delete_room, name='delete_room'),
    path('admin-panel/rooms/<int:pk>/image/', v.upload_room_image, name='upload_room_image'),
    path('admin-panel/rooms/<int:pk>/image/delete/', v.delete_room_image, name='delete_room_image'),
    path('admin-panel/reports/', v.admin_reports, name='admin_reports'),
    path('admin-panel/reports/csv/', v.reports_csv, name='reports_csv'),
    path('admin-panel/users/', v.admin_users, name='admin_users'),
    path('admin-panel/users/<int:user_id>/role/', v.set_user_role, name='set_user_role'),
    path('admin-panel/ai/', v.admin_ai_page, name='admin_ai_page'),
    path('admin-panel/ai/chat/', v.admin_ai_chat, name='admin_ai_chat'),

    # Blackout Period (FR-ADM-03)
    path('admin-panel/blackout/', v.admin_blackout, name='admin_blackout'),
    path('admin-panel/blackout/add/', v.add_blackout, name='add_blackout'),
    path('admin-panel/blackout/<int:pk>/edit/', v.edit_blackout, name='edit_blackout'),
    path('admin-panel/blackout/<int:pk>/delete/', v.delete_blackout, name='delete_blackout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)