# django
from django.db import models
from django.contrib.auth.models import User, PermissionsMixin, AbstractBaseUser, BaseUserManager

# Models
from apps.ubigeo.models import Department, Province, District
from apps.default.models import Entity, Departments

class Person(models.Model):
    CHOICES_TYPE_SEX = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    )

    CHOICES_TYPE_CIVIL = (
        ('S', 'Soltero'),
        ('C', 'Casado'),
        ('V', 'Viudo'),
        ('D', 'Divorciado'),
        ('O', 'Otros')
    )

    CHOICES_TYPE_DOC = (
        ('D', 'DNI'),
        ('P', 'PASAPORTE')
    )

    eid           = models.ForeignKey(Entity, on_delete=models.PROTECT)
    docid         = models.CharField(max_length=20)
    typedoc       = models.CharField(max_length=1, choices=CHOICES_TYPE_DOC)
    last_name0    = models.CharField(max_length=150)
    last_name1    = models.CharField(max_length=150)
    first_name    = models.CharField(max_length=150)
    birthday      = models.DateField(auto_now=False, auto_now_add=False,  null=True)
    sex           = models.CharField(max_length=1, choices=CHOICES_TYPE_SEX)
    civil         = models.CharField(max_length=2, choices=CHOICES_TYPE_CIVIL)
    mail          = models.CharField(max_length=100, null=True)
    cellphone     = models.CharField(max_length=9,   null=True)
    r_department  = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
    r_province    = models.ForeignKey(Province, on_delete=models.PROTECT, null=True, blank=True)
    r_district    = models.ForeignKey(District, on_delete=models.PROTECT, null=True, blank=True)
    address       = models.CharField(max_length=150, null=True, blank=True)
     
    user_create   = models.CharField(max_length=15)
    user_update   = models.CharField(max_length=15, null=True,blank=True,)
    date_create   = models.DateField(auto_now_add=True)
    date_update   = models.DateField(auto_now=True, blank=True, null=True)

    def natural_key(self):
        return self.pk, self.last_name0, self.last_name1, self.first_name,\
               self.docid, self.birthday, self.sex, self.civil, self.mail, self.address

    def __str__(self):
        return '%s %s, %s' % (self.last_name0,self.last_name1, self.first_name )
    
    class Meta:
        unique_together = ['eid', 'docid']

class UserProfileManager(BaseUserManager):

    def create_user(self, username, password=None):
        if not username:
            raise ValueError('El usuario debe tener un usuario para acceso')

        user          = self.model()
        user.username = username
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, username,  password=None):
        user          = self.create_user(username, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser,PermissionsMixin):
    
    username = models.CharField(max_length=15, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_posta = models.BooleanField(default=False)

    docid   = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)
    depid   = models.ForeignKey(Departments, on_delete=models.CASCADE, null=True,blank=True)

    objects = UserProfileManager()

    USERNAME_FIELD = 'username'

    def natural_key(self):
            return self.pk, self.username, self.docid.pk

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "¿Tiene el usuario un permiso específico?"
        return True

    def has_module_perms(self, app_label):
        "¿Tiene el usuario permisos para ver la aplicación ʻapp_label`?"
        return True

    @property
    def is_staff(self):
        "¿El usuario es miembro del personal?"
        return self.is_admin

    def get_full_name(self):
        return '{0} {1}'.format(self.username)

    def get_short_name(self):
        return self.username
    class Meta:
        verbose_name = 'Usuario de sistema'
        verbose_name_plural = 'Usuarios del sistema'