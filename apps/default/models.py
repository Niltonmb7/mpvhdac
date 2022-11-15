#Django
from django.db import models

class Entity(models.Model):
    eid = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=250)
    legal_representative = models.CharField(max_length=250, null=True)

    user_create = models.CharField(max_length=15)
    user_update = models.CharField(max_length=15, null=True,blank=True,)
    date_create = models.DateField(auto_now_add=True)
    date_update = models.DateField(auto_now=True, blank=True, null=True)

    def natural_key(self):
        return self.pk, self.name

    def __str__(self):
        return self.name


class Departments_type(models.Model):
    tid         = models.CharField(max_length=2, primary_key=True)
    eid         = models.ForeignKey(Entity, on_delete=models.CASCADE)
    name        = models.CharField(max_length=250)
    state       = models.CharField(max_length=2, blank=True, null=True)
    order       = models.IntegerField()

    user_create = models.CharField(max_length=15)
    user_update = models.CharField(max_length=15, null=True,blank=True,)
    date_create = models.DateField(auto_now_add=True)
    date_update = models.DateField(auto_now=True, blank=True, null=True)

    def natural_key(self):
        return self.pk, self.name

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['eid', 'tid'],

class Departments(models.Model):

    eid             = models.ForeignKey(Entity, on_delete=models.CASCADE)
    depid           = models.CharField(max_length=15)
    name            = models.CharField(max_length=250)
    abbreviation    = models.CharField(max_length=20, blank=True, null=True)
    parent          = models.CharField(max_length=15, blank=True, null=True)
    state           = models.CharField(max_length=2, blank=True, null=True)
    type            = models.ForeignKey(Departments_type,on_delete=models.CASCADE)
    order           = models.IntegerField()

    user_create     = models.CharField(max_length=15)
    user_update     = models.CharField(max_length=15, null=True,blank=True,)
    date_create     = models.DateField(auto_now_add=True)
    date_update     = models.DateField(auto_now=True, blank=True, null=True)

    def natural_key(self):
        return self.pk, self.depid, self.name

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['eid', 'depid'],
