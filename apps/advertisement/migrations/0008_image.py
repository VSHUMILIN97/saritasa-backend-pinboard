# Generated by Django 2.1 on 2018-08-15 09:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('advertisement', '0002_create_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertisement',
            name='photo',
            field=models.ImageField(null=True, upload_to='backend/assets/image_ad', verbose_name='Photo'),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='backend/assets/image_ad', verbose_name='Photo')),
                ('advertisement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images',
                                                    to='advertisement.Advertisement')),
            ],
        ),
    ]
