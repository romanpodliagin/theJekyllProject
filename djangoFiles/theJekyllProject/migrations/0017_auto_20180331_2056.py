# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-31 20:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theJekyllProject', '0016_auto_20180309_2314'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='background',
            field=models.ImageField(blank=True, null=True, upload_to='pictures/'),
        ),
        migrations.AddField(
            model_name='sitedata',
            name='author',
            field=models.CharField(blank=True, default='Author of the site', max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='sitedata',
            name='baseurl',
            field=models.CharField(blank=True, default='/jekyllblog', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='sitedata',
            name='url',
            field=models.CharField(blank=True, default='http://blog.jeklog.com', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='sitedata',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]