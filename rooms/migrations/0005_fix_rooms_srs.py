from django.db import migrations

# ห้องตาม SRS Section 2.3
SRS_ROOMS = [
    ('406-3', 'ห้องประชุม 1', 'MEETING', 60),
    ('406-5', 'ห้องประชุม 2', 'MEETING', 15),
    ('408-1', 'ห้องประชุม 3', 'MEETING', 10),
    ('408-2/1', 'ห้องบรรยาย 1', 'LECTURE', 20),
    ('408-2/2', 'ห้องบรรยาย 2', 'LECTURE', 20),
]


def seed_srs_rooms(apps, schema_editor):
    Room = apps.get_model('rooms', 'Room')
    # ลบห้องเดิมที่ไม่ตรง SRS
    old_codes = ['401', '402', '403', '404', '405', '406', '408-2']
    Room.objects.filter(code__in=old_codes).delete()
    # เพิ่มห้องตาม SRS
    for code, name, room_type, capacity in SRS_ROOMS:
        Room.objects.update_or_create(
            code=code,
            defaults={
                'name': name,
                'room_type': room_type,
                'capacity': capacity,
                'is_active': True,
            },
        )


def reverse_seed(apps, schema_editor):
    Room = apps.get_model('rooms', 'Room')
    Room.objects.filter(code__in=[r[0] for r in SRS_ROOMS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('rooms', '0004_alter_room_image'),
    ]

    operations = [
        migrations.RunPython(seed_srs_rooms, reverse_seed),
    ]
