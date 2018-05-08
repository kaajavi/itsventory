# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission, Group
from django.conf import settings
from random import randint
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        '''
        Create groups and append permissions
        '''
        #USER PERMISSION:
        aus = Permission.objects.get(codename='add_user')
        cus = Permission.objects.get(codename='change_user')
        dus = Permission.objects.get(codename='delete_user')

        #PROFILE USER PERMISSION
        apu = Permission.objects.get(codename='add_userprofile')
        cpu = Permission.objects.get(codename='change_userprofile')
        dpu = Permission.objects.get(codename='delete_userprofile')

        #VCARD PERMISSION
        avc = Permission.objects.get(codename='add_vcard')
        cvc = Permission.objects.get(codename='change_vcard')
        dvc = Permission.objects.get(codename='delete_vcard')



        admin = Group.objects.get_or_create(id=1)[0]
        admin.permissions.set([aus,cus,
                               apu,cpu,
                               avc,cvc,dvc
                              ])
        admin.name='Administradores'
        admin.save()

        section = Group.objects.get_or_create(id=2)[0]
        section.permissions.set([aus,cus,
                               apu,cpu,
                               avc,cvc,dvc
                              ])
        section.name='Jefes de Sección'
        section.save()

        employed = Group.objects.get_or_create(id=3)[0]
        employed.permissions.set([apu,cpu,
                               avc,cvc,dvc
                              ])
        employed.name='Usuarios Finales'
        employed.save()



        for u in User.objects.all():
            u.reset_group()
