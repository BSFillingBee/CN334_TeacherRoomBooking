from datetime import date, time
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings

from bookings.models import Booking
from rooms.models import Room
from room_booking import template_views


class BookingValidationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='lecturer', password='pass')
        self.room = Room.objects.create(
            code='TEST-101',
            name='Test Room',
            room_type='LECTURE',
            capacity=30,
        )

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_teaching_booking_requires_program(self):
        self.client.force_login(self.user)
        response = self.client.post('/bookings/new/', {
            'roomId': self.room.id,
            'startDate': '2030-01-07',
            'endDate': '2030-01-07',
            'daysOfWeek': '0',
            'startTime': '09:00',
            'endTime': '10:00',
            'purposeType': 'TEACHING',
            'courseId': 'CN334',
            'courseName': 'Software Engineering',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'หลักสูตร')
        self.assertEqual(Booking.objects.count(), 0)


class AdminReportOccurrenceTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = get_user_model().objects.create_user(username='admin', password='pass', role='ADMIN')
        self.lecturer = get_user_model().objects.create_user(username='lecturer', password='pass')
        self.room = Room.objects.create(
            code='TEST-201',
            name='Report Room',
            room_type='LECTURE',
            capacity=40,
        )

    def test_admin_report_counts_recurring_occurrences_and_hours(self):
        Booking.objects.create(
            requester=self.lecturer,
            room=self.room,
            purpose_type='TEACHING',
            course_id='CN334',
            course_name='Software Engineering',
            program='NORMAL',
            start_date=date(2030, 1, 7),
            end_date=date(2030, 1, 21),
            days_of_week='0',
            start_time=time(9, 0),
            end_time=time(11, 0),
            status='APPROVED',
        )
        request = self.factory.get('/admin-panel/reports/?start=2030-01-01&end=2030-01-31')
        request.user = self.admin

        with patch.object(template_views, 'render', side_effect=lambda request, template, context: context):
            context = template_views.admin_reports(request)

        report_room = next(room for room in context['by_room'] if room['code'] == self.room.code)
        self.assertEqual(report_room['count'], 3)
        self.assertEqual(report_room['hours'], 6.0)
        self.assertEqual(context['summary']['total'], 3)
        self.assertEqual(context['summary']['hours'], 6.0)
