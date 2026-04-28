from django.db import migrations


DEFAULT_ROOMS = [
    ('401', 'ห้องประชุมสภาคณะ', 'MEETING', 24),
    ('402', 'ห้องสัมมนา A', 'MEETING', 20),
    ('403', 'ห้องสัมมนา B', 'MEETING', 16),
    ('404', 'ห้องประชุมย่อย 1', 'MEETING', 6),
    ('405', 'ห้องประชุมย่อย 2', 'MEETING', 8),
    ('406', 'ห้อง Co-Working', 'MEETING', 12),
]


def seed_rooms(apps, schema_editor):
    Room = apps.get_model('rooms', 'Room')
    for code, name, room_type, capacity in DEFAULT_ROOMS:
        Room.objects.update_or_create(
            code=code,
            defaults={
                'name': name,
                'room_type': room_type,
                'capacity': capacity,
                'is_active': True,
            },
        )


def unseed_rooms(apps, schema_editor):
    Room = apps.get_model('rooms', 'Room')
    Room.objects.filter(code__in=[room[0] for room in DEFAULT_ROOMS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('rooms', '0002_auto_20260421_1512'),
    ]

    operations = [
        migrations.RunPython(seed_rooms, unseed_rooms),
    ]
