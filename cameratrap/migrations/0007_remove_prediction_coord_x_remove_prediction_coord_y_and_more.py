# Generated by Django 4.1.7 on 2023-03-21 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cameratrap', '0006_videofile_video_height_videofile_video_width_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prediction',
            name='coord_x',
        ),
        migrations.RemoveField(
            model_name='prediction',
            name='coord_y',
        ),
        migrations.AddField(
            model_name='prediction',
            name='coord_bottom',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='prediction',
            name='coord_left',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='prediction',
            name='coord_right',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='prediction',
            name='coord_top',
            field=models.IntegerField(default=0),
        ),
    ]
