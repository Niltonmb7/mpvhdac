from django.contrib import admin

# Register your models here.
from .models import Country, Department, Province, District

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):

    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = ('name', 'code', 'country')
    search_fields = ('name', 'pais__nombre')

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):

    list_display = ('name', 'code', 'departament')
    search_fields = ('name', 'departamento__nombre')

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):

    list_display = ('name', 'code', 'province')
    search_fields = ('name', 'provincia__nombre')