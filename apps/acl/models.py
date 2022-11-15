#Django
from django.db import models
from django.contrib.auth.models import Permission, Group

class Menu(models.Model):
    name        = models.CharField(max_length=250)
    icon        = models.CharField(max_length=100, null=True)
    order       = models.IntegerField()
    state       = models.CharField(max_length=1, default='B')

    def natural_key(self):
        return self.pk, self.name

    def __str__(self):
        return self.name

class Permissionmenu(models.Model):
    permission = models.OneToOneField(Permission, primary_key=True, on_delete=models.PROTECT)
    menu       = models.ForeignKey(Menu, on_delete=models.CASCADE)
    order      = models.IntegerField()

    def __str__(self):
        return self.permission

class Modules(models.Model):
    TYPE_MODULE = (
        ('DESARROLLADO', 'DESARROLLADO'),
        ('GESTIONADO', 'GESTIONADO')
    )
    name        = models.CharField(max_length=250)
    app_name    = models.CharField(max_length=200 ,blank=True, null=True)
    route       = models.CharField(max_length=250,blank=True, null=True)
    order       = models.IntegerField()
    parent      = models.CharField(max_length=15, blank=True, null=True)
    state       = models.BooleanField(default=True)
    url_external= models.URLField(max_length=250, blank=True, null=True)
    color       = models.CharField(max_length=100 ,blank=True, null=True)
    icon        = models.CharField(max_length=500 ,blank=True, null=True)
    type_module = models.CharField(max_length=20, choices=TYPE_MODULE, blank=True, null=True)

    def natural_key(self):
        return self.pk, self.name, self.app_name, self.route, self.order, self.parent

    def __str__(self):
        return self.name

class ModuleGroup(models.Model):
    module      = models.ForeignKey(Modules, on_delete=models.CASCADE)
    group       = models.ForeignKey(Group, on_delete=models.CASCADE)