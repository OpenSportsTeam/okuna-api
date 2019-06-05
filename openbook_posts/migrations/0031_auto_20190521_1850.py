# Generated by Django 2.2 on 2019-05-21 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openbook_posts', '0030_post_is_closed'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
