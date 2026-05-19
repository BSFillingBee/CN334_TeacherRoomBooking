from django.test import TestCase

from rooms.models import Room


class InitialRoomSeedTests(TestCase):
    def test_initial_rooms_are_seeded_by_migration(self):
        expected = {
            '406-3': ('ห้องประชุม 1', 'MEETING', 60),
            '406-5': ('ห้องประชุม 2', 'MEETING', 15),
            '408-1': ('ห้องประชุม 3', 'MEETING', 10),
            '408-2/1': ('ห้องบรรยาย 1', 'LECTURE', 20),
            '408-2/2': ('ห้องบรรยาย 2', 'LECTURE', 20),
        }

        rooms = Room.objects.in_bulk(expected.keys(), field_name='code')

        self.assertEqual(set(rooms.keys()), set(expected.keys()))
        for code, (name, room_type, capacity) in expected.items():
            with self.subTest(code=code):
                room = rooms[code]
                self.assertEqual(room.name, name)
                self.assertEqual(room.room_type, room_type)
                self.assertEqual(room.capacity, capacity)
                self.assertTrue(room.is_active)
