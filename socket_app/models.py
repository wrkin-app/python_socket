from django.db import models
from django.contrib.postgres.fields import ArrayField,JSONField
from django.utils import timezone

# Create your models here.

class CompanyProfile(models.Model):
    name = models.TextField(blank=True, null=True)
    logo = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    no_of_emp = models.IntegerField(blank=True, null=True)
    type_of_org = models.TextField(blank=True, null=True)
    reg_id = models.TextField(blank=True, null=True)
    country_code = models.IntegerField(blank=True, null=True)
    phone_no = models.BigIntegerField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    is_enabled = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'company_profile'

class Designations(models.Model):
    company_profile = models.ForeignKey('CompanyProfile', models.DO_NOTHING, db_column='company_profile', blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    is_enabled = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'designations'

class CustomerUser(models.Model):
    name = models.TextField(blank=True, null=True)
    country_code = models.IntegerField(blank=True, null=True)
    phone_no = models.BigIntegerField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)  # This field type is a guess.
    designations = models.ForeignKey('Designations', models.DO_NOTHING, db_column='designations', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    company_profile = models.ForeignKey('CompanyProfile', models.DO_NOTHING, db_column='company_profile', blank=True, null=True)
    secure_token = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    is_enabled = models.BooleanField(blank=True, null=True)
    is_admin = models.BooleanField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Convert the provided Indian datetime to UTC
        date_time = timezone.localtime(self.last_login_at, timezone=timezone.get_current_timezone())
        self.created_at = date_time
        self.updated_at = date_time
        
        super().save(*args, **kwargs)

    class Meta:
        managed = False
        db_table = 'customer_user'

class OtpVerify(models.Model):
    country_code = models.IntegerField(blank=True, null=True)
    phone_no = models.BigIntegerField(blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
    try_count = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'otp_verify'

class Rooms(models.Model):
    id = models.BigAutoField(primary_key=True)
    users = ArrayField(models.IntegerField(), blank=True, null=True)
    active_users = ArrayField(models.IntegerField(), blank=True, null=True)
    is_enabled = models.BooleanField(blank=True, null=True)
    is_group = models.BooleanField(blank=True, null=True)
    group_name = models.TextField(blank=True, null=True)
    chat_name = models.JSONField(blank=True, null=True)
    admin = models.ForeignKey('CustomerUser', models.DO_NOTHING, db_column='admin', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rooms'

class Chats(models.Model):
    room = models.ForeignKey('Rooms', models.DO_NOTHING, db_column='room', blank=True, null=True)
    user = models.ForeignKey('CustomerUser', models.DO_NOTHING, db_column='user', blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    is_enabled = models.BooleanField(blank=True, null=True)
    unread_users = ArrayField(models.IntegerField(), blank=True, null=True)
    is_task = models.BooleanField(blank=True, null=True)
    task = models.ForeignKey('Task', models.DO_NOTHING, db_column='task', blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chats'


class Task(models.Model):
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    from_user = models.ForeignKey('CustomerUser', models.DO_NOTHING, db_column='from', blank=True, null=True)  # Field renamed because it was a Python reserved word.
    to_user = models.ForeignKey('CustomerUser', models.DO_NOTHING, db_column='to', related_name='task_to_set', blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    priority = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task'