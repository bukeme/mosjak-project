# Generated by Django 3.2.16 on 2022-12-02 20:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spa', '0002_auto_20221201_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='spa.project'),
        ),
    ]
