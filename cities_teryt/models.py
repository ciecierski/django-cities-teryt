# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from autoslug import AutoSlugField

try:
    # problem with "ł" char in slug
    from unidecode import unidecode
except ImportError:
    raise ImportError('Required Unidecode for proper diacritics encode.')

__all__ = ['Province', 'County', 'Municipality', 'Place', 'City', 'Village', 'District', ]


class Base(models.Model):
    """
    Base model for all models
    """
    id = models.CharField(primary_key=True, max_length=7)
    name = models.CharField(_('Name'), max_length=200, db_index=True)
    slug = AutoSlugField(populate_from='name', always_update=True, db_index=True)
    teryt_date = models.DateField(_('TERYT date'))
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    modified = models.DateTimeField(_('Modified'), auto_now=True)

    class Meta:
        abstract = True
        ordering = ('name',)
        unique_together = ('id', 'name')

    def __str__(self):
        return self.name + " " + self.id

    def get_display_name(self):
        name = self.name
        parent = self.parent.get_display_name()
        if name in parent:
            return u'{parent}'.format(parent=parent)
        return u'{name}, {parent}'.format(name=name, parent=parent)

    @classmethod
    def _check_model(cls):
        errors = []
        return errors
        
class Province(Base):
    """
    Province (Województwo) model.
    """
    class Meta:
        verbose_name = _('Województwo')
        verbose_name_plural = _('Województwa')

    @property
    def parent(self):
        return None

    def get_display_name(self):
        return u'{}'.format(self.name)


class County(Base):
    """
    County (Powiat) model.
    """
    province = models.ForeignKey(Province, verbose_name=_('Województwo'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Powiat')
        verbose_name_plural = _('Powiaty')

    @property
    def parent(self):
        return self.province


class Municipality(Base):
    """
    Municipality (Gmina) model.
    """
    MUNICIPALITY_TYPE_CHOICES = (
        ('1', 'gmina miejska'),
        ('2', 'gmina wiejska'),
        ('3', 'gmina miejsko-wiejska'),
        ('4', 'miasto w gminie miejsko-wiejskiej'),
        ('5', 'obszar wiejski w gminie miejsko-wiejskiej'),
    )
    province = models.ForeignKey(Province, verbose_name=_('Województwo'), on_delete=models.CASCADE)
    county = models.ForeignKey(County, verbose_name=_('Powiat'), on_delete=models.CASCADE)
    type = models.CharField(verbose_name=_('Typ gminy'), max_length=1, choices=MUNICIPALITY_TYPE_CHOICES)

    class Meta:
        verbose_name = _('Gmina')
        verbose_name_plural = _('Gminy')

    @property
    def parent(self):
        return self.county


class Place(Base):
    """
    Place (Miejscowość) model.

    Base model for places.
    """
    CITY = '96'
    VILLAGE = '01'
    PLACE_TYPE_CHOICES = (
        (CITY, _('miasto')),
        (VILLAGE, _('wieś')),
    )
    province = models.ForeignKey(Province, verbose_name=_('Województwo'), on_delete=models.CASCADE)
    county = models.ForeignKey(County, verbose_name=_('Powiat'), on_delete=models.CASCADE)
    municipality = models.ForeignKey(Municipality, verbose_name=_('Gmina'), on_delete=models.CASCADE)
    type = models.CharField(_('Type'), max_length=2, choices=PLACE_TYPE_CHOICES)

    class Meta:
        verbose_name = _('Miejscowość')
        verbose_name_plural = _('Miejscowości')

    @property
    def parent(self):
        return self.municipality


class CityManager(models.Manager):
    def get_query_set(self):
        return super(CityManager, self).get_query_set().filter(type='96')


class City(Place):
    """
    City (Miasto) model.
    """
    objects = CityManager()

    class Meta:
        proxy = True
        verbose_name = _('Miasto')
        verbose_name_plural = _('Miasta')


class VillageManager(models.Manager):
    def get_query_set(self):
        return super(VillageManager, self).get_query_set().filter(type='01')


class Village(Place):
    """
    Village (Wieś) model.
    """
    objects = VillageManager()

    class Meta:
        proxy = True
        verbose_name = _('Wieś')
        verbose_name_plural = _('Wsie')


class District(Base):
    """
    District (Dzielnica) model.
    """
    province = models.ForeignKey(Province, verbose_name=_('Wojwództwo'), on_delete=models.CASCADE)
    county = models.ForeignKey(County, verbose_name=_('Powiat'), on_delete=models.CASCADE)
    municipality = models.ForeignKey(Municipality, verbose_name=_('Gmina'), on_delete=models.CASCADE)
    city = models.ForeignKey(City, verbose_name=_('Miasto'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Dzielnica')
        verbose_name_plural = _('Dzielnice')

    @property
    def parent(self):
        return self.city
