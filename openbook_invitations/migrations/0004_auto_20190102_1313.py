# Generated by Django 2.1.4 on 2019-01-02 12:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('openbook_invitations', '0003_auto_20190102_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinvite',
            name='invited_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invited_users', to=settings.AUTH_USER_MODEL),
        ),
    ]