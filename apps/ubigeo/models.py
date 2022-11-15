# Create your models here.

from django.db import models

class Country(models.Model):

    code = models.CharField(verbose_name='Codigo', max_length=3)
    name = models.CharField(verbose_name='Nombre', max_length=100, null=False)

    class Meta:
        ordering = ["name"]
        verbose_name = "País"
        verbose_name_plural = "Paises"

    def natural_key(self):
        return (self.pk, self.name)

    def __str__(self):
        return self.name


class Department(models.Model):

    code = models.CharField(verbose_name='Codigo', max_length=6, blank=True)
    name = models.CharField(verbose_name='Nombre', max_length=100, null=False)
    country = models.ForeignKey(Country, verbose_name='Pais', blank=False, null=False, on_delete=models.CASCADE)

    class Meta:
        ordering = ["name"]
        verbose_name = u'Departameto'
        verbose_name_plural = u'Departamentos'

    def natural_key(self):
        return self.pk, self.name
    
    def __str__(self):
        return self.name


class Province(models.Model):

    code = models.CharField(verbose_name='Codigo', max_length=6, blank=True)
    name = models.CharField(verbose_name='Nombre', max_length=100, null=False)
    departament = models.ForeignKey(Department, verbose_name='Departamento', blank=False, null=False, on_delete=models.CASCADE)

    class Meta:
        ordering = ["name"]
        verbose_name = u'Provincia'
        verbose_name_plural = u'Provincias'

    def natural_key(self):
        return self.pk, self.name

    def __str__(self):
        return self.name


class District(models.Model):

    code = models.CharField(verbose_name='Codigo', max_length=6, blank=True)
    name = models.CharField(verbose_name='Nombre', max_length=100,null=False)
    province = models.ForeignKey(Province, verbose_name='Provincia', blank=False, null=False, on_delete=models.CASCADE)

    class Meta:
        ordering = ["name"]
        verbose_name = u'Distrito'
        verbose_name_plural= u'Distritos'

    def natural_key(self):
        return self.pk, self.name
    
    def __str__(self):
        return self.name
