# Generated by Django 4.2.1 on 2023-06-03 22:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('product', '0001_initial')]

    operations = [
        migrations.RemoveField(model_name='product', name='material'),
        migrations.AddField(
            model_name='product', name='material', field=models.ManyToManyField(to='product.materials')
        ),
    ]
