# Generated by Django 3.0.8 on 2022-07-06 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_fix_url_to_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='level',
            field=models.PositiveIntegerField(choices=[(2, '황금 접시'), (3, '은접시'), (4, '유리접시'), (5, '종이접시')], default=5),
        ),
    ]