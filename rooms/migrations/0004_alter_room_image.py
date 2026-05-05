from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('rooms', '0003_seed_default_rooms'),
    ]
    operations = [
        migrations.AlterField(
            model_name='room',
            name='image',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='รูปภาพห้อง (URL)'),
        ),
    ]
