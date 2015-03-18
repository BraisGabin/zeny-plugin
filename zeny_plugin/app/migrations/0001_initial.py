# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import zeny_plugin.app.models
from django.conf import settings
import django.core.validators


def get_sql(file_name):
    with open("zeny_plugin/app/migrations/" + file_name, "r") as sql:
        return sql.read()


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunSQL(get_sql('rathena.sql')),
        migrations.RunSQL(get_sql('zeny.sql')),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True, db_column=b'account_id')),
                ('name', models.CharField(unique=True, max_length=23, db_column=b'userid')),
                ('user_pass', models.CharField(max_length=32)),
                ('sex', models.CharField(max_length=1)),
                ('email', models.CharField(max_length=39)),
                ('group_id', models.IntegerField()),
                ('state', models.IntegerField()),
                ('unban_time', models.IntegerField()),
                ('expiration_time', models.IntegerField()),
                ('logincount', models.IntegerField()),
                ('lastlogin', models.DateTimeField()),
                ('last_ip', models.CharField(max_length=100)),
                ('birthdate', models.DateField()),
                ('character_slots', models.IntegerField()),
                ('pincode', models.CharField(max_length=4)),
                ('pincode_change', models.IntegerField()),
                ('bank_vault', models.IntegerField()),
                ('vip_time', models.IntegerField()),
                ('old_group', models.IntegerField()),
            ],
            options={
                'db_table': 'login',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Char',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True, db_column=b'char_id')),
                ('name', models.CharField(unique=True, max_length=30)),
                ('job', models.IntegerField(default=0, db_column=b'class')),
                ('zeny', models.IntegerField(default=0)),
                ('online', models.IntegerField(default=0)),
                ('fame', models.IntegerField(default=0)),
                ('delete_date', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'char',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('type', models.PositiveIntegerField()),
            ],
            options={
                'db_table': 'item_db_re',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('nameid', models.IntegerField()),
                ('amount', models.PositiveIntegerField(validators=[zeny_plugin.app.models.strictly_positive, django.core.validators.MaxValueValidator(30000)])),
                ('equip', models.IntegerField()),
                ('identify', models.IntegerField()),
                ('refine', models.IntegerField()),
                ('attribute', models.IntegerField()),
                ('card0', models.IntegerField()),
                ('card1', models.IntegerField()),
                ('card2', models.IntegerField()),
                ('card3', models.IntegerField()),
                ('expire_time', models.IntegerField()),
                ('bound', models.IntegerField()),
                ('unique_id', models.BigIntegerField()),
            ],
            options={
                'db_table': 'storage',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vending',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('nameid', models.IntegerField()),
                ('amount', models.PositiveIntegerField(validators=[zeny_plugin.app.models.strictly_positive, django.core.validators.MaxValueValidator(30000)])),
                ('equip', models.IntegerField()),
                ('identify', models.IntegerField()),
                ('refine', models.IntegerField()),
                ('attribute', models.IntegerField()),
                ('card0', models.IntegerField()),
                ('card1', models.IntegerField()),
                ('card2', models.IntegerField()),
                ('card3', models.IntegerField()),
                ('expire_time', models.IntegerField()),
                ('bound', models.IntegerField()),
                ('unique_id', models.BigIntegerField()),
                ('zeny', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(1000000000)])),
            ],
            options={
                'db_table': 'storage_vending',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VendingLog',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('nameid', models.IntegerField()),
                ('refine', models.IntegerField()),
                ('card0', models.IntegerField()),
                ('card1', models.IntegerField()),
                ('card2', models.IntegerField()),
                ('card3', models.IntegerField()),
                ('amount', models.PositiveIntegerField(validators=[zeny_plugin.app.models.strictly_positive, django.core.validators.MaxValueValidator(30000)])),
                ('zeny', models.PositiveIntegerField(validators=[zeny_plugin.app.models.strictly_positive, django.core.validators.MaxValueValidator(1000000000)])),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'vending_log',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Zeny',
            fields=[
                ('id', models.OneToOneField(related_name='zeny_vending', primary_key=True, db_column=b'id', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('zeny', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(1000000000)])),
            ],
            options={
                'db_table': 'zeny',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
