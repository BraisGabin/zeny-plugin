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
                ('char_num', models.IntegerField()),
                ('name', models.CharField(unique=True, max_length=30)),
                ('class_field', models.IntegerField(db_column=b'class')),
                ('base_level', models.IntegerField()),
                ('job_level', models.IntegerField()),
                ('base_exp', models.BigIntegerField()),
                ('job_exp', models.BigIntegerField()),
                ('zeny', models.IntegerField()),
                ('str', models.IntegerField()),
                ('agi', models.IntegerField()),
                ('vit', models.IntegerField()),
                ('int', models.IntegerField()),
                ('dex', models.IntegerField()),
                ('luk', models.IntegerField()),
                ('max_hp', models.IntegerField()),
                ('hp', models.IntegerField()),
                ('max_sp', models.IntegerField()),
                ('sp', models.IntegerField()),
                ('status_point', models.IntegerField()),
                ('skill_point', models.IntegerField()),
                ('option', models.IntegerField()),
                ('karma', models.IntegerField()),
                ('manner', models.IntegerField()),
                ('party_id', models.IntegerField()),
                ('guild_id', models.IntegerField()),
                ('pet_id', models.IntegerField()),
                ('homun_id', models.IntegerField()),
                ('elemental_id', models.IntegerField()),
                ('hair', models.IntegerField()),
                ('hair_color', models.IntegerField()),
                ('clothes_color', models.IntegerField()),
                ('weapon', models.IntegerField()),
                ('shield', models.IntegerField()),
                ('head_top', models.IntegerField()),
                ('head_mid', models.IntegerField()),
                ('head_bottom', models.IntegerField()),
                ('robe', models.IntegerField()),
                ('last_map', models.CharField(max_length=11)),
                ('last_x', models.IntegerField()),
                ('last_y', models.IntegerField()),
                ('save_map', models.CharField(max_length=11)),
                ('save_x', models.IntegerField()),
                ('save_y', models.IntegerField()),
                ('partner_id', models.IntegerField()),
                ('online', models.IntegerField()),
                ('father', models.IntegerField()),
                ('mother', models.IntegerField()),
                ('child', models.IntegerField()),
                ('fame', models.IntegerField()),
                ('rename', models.IntegerField()),
                ('delete_date', models.IntegerField()),
                ('moves', models.IntegerField()),
                ('unban_time', models.IntegerField()),
                ('font', models.IntegerField()),
                ('uniqueitem_counter', models.IntegerField()),
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
                ('buyer', models.ForeignKey(related_name='shopping', db_column=b'buyer_account_id', to=settings.AUTH_USER_MODEL)),
                ('seller', models.ForeignKey(related_name='sales', db_column=b'seller_account_id', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'vending_log',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
