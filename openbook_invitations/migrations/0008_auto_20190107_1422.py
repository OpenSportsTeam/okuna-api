# Generated by Django 2.1.5 on 2019-01-07 13:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('openbook_invitations', '0007_auto_20190106_0205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinvite',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='email address'),
        ),
        migrations.AlterUniqueTogether(
            name='userinvite',
            unique_together={('invited_by', 'email')},
        ),
    ]
