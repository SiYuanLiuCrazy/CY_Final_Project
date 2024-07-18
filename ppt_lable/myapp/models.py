from django.db import models
import uuid

class TyPptCatalog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent_id = models.UUIDField(null=True, blank=True)
    label = models.CharField(max_length=64, default='')
    path = models.CharField(max_length=1024, default='')

    status = models.CharField(max_length=64, default='sys_status.OK')
    order_num = models.IntegerField(default=0)
    remark = models.CharField(max_length=1024, default='', blank=True)
    deleted_flag = models.BooleanField(default=False)
    created_by = models.CharField(max_length=64, default='', blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=64, default='', blank=True)
    updated_time = models.DateTimeField(auto_now=True, null=True)
    deleted_by = models.CharField(max_length=64, default='', blank=True)
    deleted_time = models.DateTimeField(null=True, blank=True)

    @property
    def children(self):
        return TyPptCatalog.objects.filter(parent_id=self.id)

    class Meta:
        db_table = 'ty_ppt_catalog'

class TyPptMain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=64, default='')
    lable = models.CharField(max_length=64, default='')
    catalog = models.UUIDField(null=True, blank=True)
    name = models.CharField(max_length=1024, default='')
    type = models.CharField(max_length=64, default='')
    size = models.BigIntegerField(null=True, blank=True)
    path = models.CharField(max_length=1024, default='')

    status = models.CharField(max_length=64, default='sys_status.OK')
    order_num = models.IntegerField(default=0)
    remark = models.CharField(max_length=1024, default='', blank=True)
    deleted_flag = models.BooleanField(default=False)
    created_by = models.CharField(max_length=64, default='', blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=64, default='', blank=True)
    updated_time = models.DateTimeField(null=True, blank=True)
    deleted_by = models.CharField(max_length=64, default='', blank=True)
    deleted_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ty_ppt_main'