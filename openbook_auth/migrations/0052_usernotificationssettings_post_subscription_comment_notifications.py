# Generated by Django 2.2.5 on 2020-02-26 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openbook_auth', '0051_auto_20191209_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernotificationssettings',
            name='post_subscription_comment_notifications',
            field=models.BooleanField(default=True, verbose_name='post subscription comment notifications'),
        ),
    ]
