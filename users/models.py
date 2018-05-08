# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.utils.translation import ugettext_lazy as _
from django.utils import six, timezone
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.staticfiles.templatetags.staticfiles import static

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='image_users/',
                              default='image_users/default.png', blank=True)
    photo_social = models.URLField(max_length=1000, null=True, blank=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '{} {}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_picture(self):
        "Determines which picture the client should use."

        if self.photo and self.photo_social and self.photo.name.endswith("default.png"):
            return self.photo_social
        elif self.photo:
            return self.photo.url
        return ''

    def set_vcards(self, vcards):
        """
        Expects a list of vcards like [{'type_of_card':'xxx', 'data':'xxx'},]
        Deletes previous vcards, and sets the new ones.
        """
        self.vcards.all().delete()
        for vcard in vcards:
            new_vcard = VCard()
            new_vcard.type_of_card = vcard['type_of_card']
            new_vcard.data = vcard['data']
            new_vcard.user = self
            new_vcard.save()

    def __str__(self):
        return self.get_full_name()


class VCard(models.Model):
    '''
    Generic contact card.
    '''
    TYPES_AVAILABLES=(
        ('email','Email'),
        ('phone','Teléfono'),
        ('address','Dirección'),
    )

    type_of_card = models.CharField("Tipo de dato",
        choices=TYPES_AVAILABLES,
        max_length=20)
    data = models.CharField("Valor", max_length=128)
    upload_date = models.DateTimeField('Last change', auto_now=True)
    user = models.ForeignKey(UserProfile, related_name='vcards', null=True, blank=True)

    def vcard_icon(self):
        from django.utils.html import format_html
        type_of_card = self.type_of_card
        if type_of_card == 'email':
            return format_html('<i class="material-icons">email</i>')
        if type_of_card == 'phone':
            return format_html('<i class="material-icons">phone</i>')
        if type_of_card == 'address':
            return format_html('<i class="material-icons">person_pin</i>')
        if type_of_card == 'link':
            return format_html('<i class="material-icons">public</i>')

    def vcard_html(self):
        from django.utils.html import format_html
        type_of_card = self.type_of_card
        if type_of_card == 'email':
            return format_html('<a href="mailto:{}">{}</a>'.format(self.data,self.data))
        if type_of_card == 'phone':
            return format_html('<a href="tel:{}">{}</a>'.format(self.data,self.data))
        if type_of_card == 'address':
            return format_html(self.data)
        if type_of_card == 'link':
            return format_html('<a href="{}">{}</a>'.format(self.data,self.data))

    def __unicode__(self):
        return self.type_of_card + ': ' + self.data

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, email=None, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, email=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)


# A few helper functions for common logic between User and AnonymousUser.
def _user_get_all_permissions(user, obj):
    permissions = set()
    for backend in auth.get_backends():
        if hasattr(backend, "get_all_permissions"):
            permissions.update(backend.get_all_permissions(user, obj))
    return permissions


def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_perm'):
            continue
        try:
            if backend.has_perm(user, perm, obj):
                return True
        except PermissionDenied:
            return False
    return False


def _user_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_module_perms'):
            continue
        try:
            if backend.has_module_perms(user, app_label):
                return True
        except PermissionDenied:
            return False
    return False

class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),

    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

class User(AbstractUser):
    '''
        Agregar al usuario el tipo de usuario.
    '''
    ADMIN = 1
    SECTION = 2
    EMPLOYED = 3
    INVITED = 4


    USERS_TYPE =  [
        (ADMIN, 'Administrador'),
        (SECTION, 'Jefe de Área'),
        (EMPLOYED, 'Editor'),
        (INVITED, 'Visor'),
    ]

    user_type = models.IntegerField('Tipo de Usuario', choices=USERS_TYPE, default=EMPLOYED)

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        up = UserProfile.objects.get_or_create(user=self)[0]
        if (len(up.get_full_name())>0):
            return up.get_full_name()
        return self.username.strip()
    get_full_name.short_description = 'Nombre Completo'


    def get_short_name(self):
        '''
        Returns the short name for the user. (username)
        '''
        up = UserProfile.objects.get_or_create(user=self)[0]
        if (len(up.get_short_name())>0):
            return up.get_short_name()
        return self.username.strip()

    def user_type_label(self):
        return dict(self.USERS_TYPE)[self.user_type]

    @property
    def is_administrator(self):
        return self.user_type == User.ADMIN

    @property
    def is_boss_of_section(self):
        return self.user_type == User.SECTION

    @property
    def is_employed(self):
        return self.user_type == User.EMPLOYED

    def save(self, *args, **kwargs):
        if self.id == None:
            super(User, self).save(*args, **kwargs)
            grupo = Group.objects.get(pk=self.user_type)
            self.groups.set([grupo])
            if (self.user_type>self.EMPLOYED):
                self.is_staff = False
        super(User, self).save(*args, **kwargs)

    def reset_group(self):
        grupo = Group.objects.get(pk=self.user_type)
        self.groups.set([grupo])
        if (self.user_type>self.EMPLOYED):
                self.is_staff = False
        self.save()


#    def get_url_css_material(self):
#
#        "Retorna las url de los css que utiliza materialize"
#        return static('material/css/materialize-{}.css'.format(self.get_store_color()))
#
#    def get_url_css_base(self):
#        "Retorna las url de los css que utiliza materialize"
#        return static('material/admin/css/base-{}.css'.format(self.get_store_color()))
#
#        '''
#        Retorna las url de los css que utiliza materialize
#        '''
#        if self.user_type >= User.MANAGER:
#            try:
#                url= static('material/css/materialize-{}.css'.format(self.my_stores()[0].color_store))
#            except Exception as e:
#                url= static('material/css/materialize-green.css')
#        else:
#            url= static('material/css/materialize-green.css')
#        return url
#
#    def get_url_css_base(self):
#        '''
#        Retorna las url de los css que utiliza materialize
#        '''
#        if self.user_type >= User.MANAGER:
#            try:
#                url = static('material/admin/css/base-{}.css'.format(self.my_stores()[0].color_store))
#            except:
#                url = static('material/admin/css/base-green.css')
#        else:
#            url = static('material/admin/css/base-green.css')
#        return url


#    def get_url_icon(self):
#        '''
#        Retorna la url del icono que tiene que mostrarse en el admin
#        '''
#        if self.user_type < User.MANAGER:
#            return static('img/logo.png')
#        try:
#            if self.my_stores()[0].logo:
#                return self.my_stores()[0].logo.url
#            return static('img/logo.png')
#        except Exception as e:
#            print "ERROR {}".format(e)
#            return static('img/logo.png')

