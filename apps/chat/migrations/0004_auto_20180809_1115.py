# Generated by Django 2.1 on 2018-08-09 11:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_auto_20180808_0533'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatmessage',
            options={'verbose_name': 'Chat message', 'verbose_name_plural': 'Chat messages'},
        ),
        migrations.AlterModelOptions(
            name='chatroom',
            options={'ordering': ('link',), 'verbose_name': 'Chat room', 'verbose_name_plural': 'Chat rooms'},
        ),
    ]
