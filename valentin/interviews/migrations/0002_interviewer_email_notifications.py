# Generated by Django 3.1.5 on 2021-03-06 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewer',
            name='email_notifications',
            field=models.BooleanField(default=False, verbose_name='Recevoir des notifications email pour mes créneaux'),
        ),
    ]
