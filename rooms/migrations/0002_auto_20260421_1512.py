from django.db import migrations

def create_initial_rooms(apps, schema_editor):
    Room = apps.get_model('rooms', 'Room')
    rooms_data = [
        {'code': '406-3', 'name': 'ห้องประชุม 1', 'room_type': 'MEETING', 'capacity': 60},
        {'code': '406-5', 'name': 'ห้องประชุม 2', 'room_type': 'MEETING', 'capacity': 15},
        {'code': '408-1', 'name': 'ห้องประชุม 3', 'room_type': 'MEETING', 'capacity': 10},
        {'code': '408-2/1', 'name': 'ห้องบรรยาย 1', 'room_type': 'LECTURE', 'capacity': 20},
        {'code': '408-2/2', 'name': 'ห้องบรรยาย 2', 'room_type': 'LECTURE', 'capacity': 20},
    ]
    for data in rooms_data:
        Room.objects.get_or_create(code=data['code'], defaults=data)

def delete_initial_rooms(apps, schema_editor):
    Room = apps.get_model('rooms', 'Room')
    Room.objects.filter(code__in=['406-3', '406-5', '408-1', '408-2/1', '408-2/2']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_rooms, delete_initial_rooms),
    ]
