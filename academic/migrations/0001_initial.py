# Generated by Django 5.0 on 2023-12-23 09:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='exam',
            fields=[
                ('exam_id', models.AutoField(primary_key=True, serialize=False)),
                ('exam_name', models.CharField(max_length=64)),
                ('exam_date', models.DateField()),
                ('exam_time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='club',
            fields=[
                ('club_id', models.AutoField(primary_key=True, serialize=False)),
                ('club_name', models.CharField(max_length=64)),
                ('club_description', models.TextField()),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='subject',
            fields=[
                ('subject_id', models.AutoField(primary_key=True, serialize=False)),
                ('subject_name', models.CharField(max_length=64)),
                ('subject_code', models.CharField(max_length=15)),
                ('teacher_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='result',
            fields=[
                ('result_id', models.AutoField(primary_key=True, serialize=False)),
                ('marks', models.IntegerField()),
                ('grade', models.CharField(max_length=2)),
                ('exam_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.exam')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('subject_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.subject')),
            ],
        ),
        migrations.CreateModel(
            name='notice',
            fields=[
                ('notice_id', models.AutoField(primary_key=True, serialize=False)),
                ('notice_title', models.CharField(max_length=64)),
                ('notice_description', models.TextField()),
                ('notice_date', models.DateField()),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('subject_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.subject')),
            ],
        ),
        migrations.AddField(
            model_name='exam',
            name='subject_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic.subject'),
        ),
    ]
