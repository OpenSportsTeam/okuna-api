# Generated by Django 2.1.5 on 2019-02-09 15:31

from django.db import migrations
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('openbook_posts', '0014_auto_20181215_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postimage',
            name='image',
            field=imagekit.models.fields.ProcessedImageField(upload_to='./media', verbose_name='image'),
        ),
    ]