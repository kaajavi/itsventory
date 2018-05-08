# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
# Create your models here.

class Inventory(models.Model):
    '''
    Modelo inventario. Tiene que tener usuarios que lo puedan ver y otros editar.
    '''
    title = models.CharField('Inventario', max_length=64, default='')
    editors = models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='inventories_can_edit')
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='inventories_can_see')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'

class Place(models.Model):
    '''
    Lugares fisicos
    '''
    title = models.CharField('Inventario', max_length=64, default='')
    inventory = models.ForeignKey(Inventory)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Lugar'
        verbose_name_plural = 'Lugares'


class Category(models.Model):
    '''
    Categorías de items
    '''
    title = models.CharField('Inventario', max_length=64, default='')
    inventory = models.ForeignKey(Inventory)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorias'

class Item(models.Model):
    '''
    Items del inventario
    '''
    title = models.CharField('Producto', max_length=64, default='')
    unit = models.CharField('Unidad', max_length=64, default='')
    inventory = models.ForeignKey(Inventory)
    category =  models.ForeignKey(Category)
    place = models.ForeignKey(Place)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

class ItemEdition(models.Model):
    '''
    Altas y bajas de artículos
    '''
    items = models.ForeignKey(Item, related_name='mod_items')
    description = models.CharField('Descripción', max_length=256, default='')
    quantity = models.IntegerField()
    type_edition = models.IntegerField(choices=((-1,'Baja'),(1,'Alta')))
    brand = models.CharField('Marca', max_length=256, default='')
    invoice = models.CharField('Factura', max_length=256, default='')
    invoice_provider = models.CharField('Proveedor', max_length=256, default='')
    payment = models.CharField('Comprado con fondos de', max_length=256, default='')
    date = models.DateField('Fecha de compra')

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Carga/Descarga'
        verbose_name_plural = 'Cargas/Descargas'





