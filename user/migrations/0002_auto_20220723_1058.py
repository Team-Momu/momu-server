# Generated by Django 3.0.8 on 2022-07-23 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mbti',
            name='mbti',
            field=models.CharField(choices=[('CIMJ', 'CIMJ'), ('CIMR', 'CIMR'), ('NIMJ', 'NIMJ'), ('CITJ', 'CITJ'), ('NIMR', 'NIMR'), ('CITR', 'CITR'), ('NITJ', 'NITJ'), ('COMJ', 'COMJ'), ('NITR', 'NITR'), ('NOMJ', 'NOMJ'), ('COMR', 'COMR'), ('NOMR', 'NOMR'), ('COTJ', 'COTJ'), ('NOTJ', 'NOTJ'), ('COTR', 'COTR'), ('NOTR', 'NOTR')], max_length=10),
        ),
    ]