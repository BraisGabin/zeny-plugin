from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager, update_last_login
from django.utils.crypto import salted_hmac

from .managers import StorageManager, VendingManager


# FIXME This is really ugly
user_logged_in.disconnect(update_last_login)


def strictly_positive(value):
    if value <= 0:
        raise ValidationError('%s is not strictly positive' % value)


class User(models.Model):
    account_id = models.PositiveIntegerField(primary_key=True)
    userid = models.CharField(max_length=23, unique=True)
    user_pass = models.CharField(max_length=32)
    sex = models.CharField(max_length=1)
    email = models.CharField(max_length=39)
    group_id = models.IntegerField()
    state = models.IntegerField()
    unban_time = models.IntegerField()
    expiration_time = models.IntegerField()
    logincount = models.IntegerField()
    lastlogin = models.DateTimeField()
    last_ip = models.CharField(max_length=100)
    birthdate = models.DateField()
    character_slots = models.IntegerField()
    pincode = models.CharField(max_length=4)
    pincode_change = models.IntegerField()
    bank_vault = models.IntegerField()
    vip_time = models.IntegerField()
    old_group = models.IntegerField()

    last_login = None
    is_active = True

    objects = BaseUserManager()

    USERNAME_FIELD = 'userid'

    class Meta:
        managed = False
        db_table = 'login'

    def set_password(self, raw_password):
        self.user_pass = raw_password

    def check_password(self, raw_password):
        return self.user_pass == raw_password

    REQUIRED_FIELDS = []

    def get_username(self):
        """Return the identifying username for this User"""
        return self.userid

    def __str__(self):
        return self.get_username()

    def natural_key(self):
        return (self.get_username(),)

    def is_anonymous(self):
        """
        Always returns False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def set_unusable_password(self):
        raise NotImplementedError('Not supported')

    def has_usable_password(self):
        raise NotImplementedError('Not supported')

    def get_full_name(self):
        raise NotImplementedError('Not supported')

    def get_short_name(self):
        raise NotImplementedError('Not supported')

    def get_session_auth_hash(self):
        """
        Returns an HMAC of the password field.
        """
        key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
        return salted_hmac(key_salt, self.user_pass).hexdigest()

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: No, always
        return False

    @property
    def online(self):
        return self.chars.exclude(online=0).exists()


class Char(models.Model):
    char_id = models.PositiveIntegerField(primary_key=True)
    account = models.ForeignKey(User, related_name="chars", db_column="account_id")
    char_num = models.IntegerField()
    name = models.CharField(unique=True, max_length=30)
    class_field = models.IntegerField(db_column='class')  # Field renamed because it was a Python reserved word.
    base_level = models.IntegerField()
    job_level = models.IntegerField()
    base_exp = models.BigIntegerField()
    job_exp = models.BigIntegerField()
    zeny = models.IntegerField()
    str = models.IntegerField()
    agi = models.IntegerField()
    vit = models.IntegerField()
    int = models.IntegerField()
    dex = models.IntegerField()
    luk = models.IntegerField()
    max_hp = models.IntegerField()
    hp = models.IntegerField()
    max_sp = models.IntegerField()
    sp = models.IntegerField()
    status_point = models.IntegerField()
    skill_point = models.IntegerField()
    option = models.IntegerField()
    karma = models.IntegerField()
    manner = models.IntegerField()
    party_id = models.IntegerField()
    guild_id = models.IntegerField()
    pet_id = models.IntegerField()
    homun_id = models.IntegerField()
    elemental_id = models.IntegerField()
    hair = models.IntegerField()
    hair_color = models.IntegerField()
    clothes_color = models.IntegerField()
    weapon = models.IntegerField()
    shield = models.IntegerField()
    head_top = models.IntegerField()
    head_mid = models.IntegerField()
    head_bottom = models.IntegerField()
    robe = models.IntegerField()
    last_map = models.CharField(max_length=11)
    last_x = models.IntegerField()
    last_y = models.IntegerField()
    save_map = models.CharField(max_length=11)
    save_x = models.IntegerField()
    save_y = models.IntegerField()
    partner_id = models.IntegerField()
    online = models.IntegerField()
    father = models.IntegerField()
    mother = models.IntegerField()
    child = models.IntegerField()
    fame = models.IntegerField()
    rename = models.IntegerField()
    delete_date = models.IntegerField()
    moves = models.IntegerField()
    unban_time = models.IntegerField()
    font = models.IntegerField()
    uniqueitem_counter = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'char'


class Storage(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    account = models.ForeignKey(User, related_name="storage", db_column="account_id")
    nameid = models.IntegerField()
    amount = models.PositiveIntegerField(validators=[strictly_positive, MaxValueValidator(settings.MAX_AMOUNT)])
    equip = models.IntegerField()
    identify = models.IntegerField()
    refine = models.IntegerField()
    attribute = models.IntegerField()
    card0 = models.IntegerField()
    card1 = models.IntegerField()
    card2 = models.IntegerField()
    card3 = models.IntegerField()
    expire_time = models.IntegerField()
    bound = models.IntegerField()
    unique_id = models.BigIntegerField()

    objects = StorageManager()

    class Meta:
        managed = False
        db_table = 'storage'


class Vending(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    account = models.ForeignKey(User, related_name="vending", db_column="account_id")
    nameid = models.IntegerField()
    amount = models.PositiveIntegerField(validators=[strictly_positive, MaxValueValidator(settings.MAX_AMOUNT)])
    equip = models.IntegerField()
    identify = models.IntegerField()
    refine = models.IntegerField()
    attribute = models.IntegerField()
    card0 = models.IntegerField()
    card1 = models.IntegerField()
    card2 = models.IntegerField()
    card3 = models.IntegerField()
    expire_time = models.IntegerField()
    bound = models.IntegerField()
    unique_id = models.BigIntegerField()
    zeny = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(settings.MAX_ZENY)])

    objects = VendingManager()

    class Meta:
        managed = False
        db_table = 'storage_vending'
