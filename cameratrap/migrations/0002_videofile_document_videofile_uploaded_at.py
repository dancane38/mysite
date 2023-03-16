# Generated by Django 4.1.7 on 2023-03-16 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cameratrap', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='videofile',
            name='document',
            field=models.FileField(null=True, upload_to='media/'),
        ),
        migrations.AddField(
            model_name='videofile',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]