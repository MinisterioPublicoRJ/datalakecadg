# Generated by Django 2.1.5 on 2019-04-01 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('methodmapping', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='methodmapping',
            name='description',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
