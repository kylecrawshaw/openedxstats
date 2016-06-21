from __future__ import unicode_literals

from django.db import models

COURSE_TYPE_CHOICES = (
    ('MOOC', 'MOOC'),
    ('SPOC', 'SPOC'),
    ('Both', 'Both'),
    ('Unknown', 'Unknown'),
)

# Models

class GeoZone(models.Model):
    """
    A model describing a geographical zone.
    """
    name = models.CharField(primary_key=True, max_length=255)

    def __unicode__(self):
        return self.name


class Language(models.Model):
    """
    A model describing a language.
    """
    name = models.CharField(primary_key=True, max_length=255)

    def __unicode__(self):
        return self.name


class Site(models.Model):
    """
    A model describing an open edX website.
    """

    # Don't use null=true for CharFields as the Django default for null text is an empty string
    # Many of the sites do not have all of these fields, which is why many can be left blank

    site_type = models.CharField(max_length=255, default='General')
    name = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, primary_key=True)
    course_count = models.IntegerField(blank=True, null=True)
    last_checked = models.DateField(blank=True, null=True)
    org_type = models.CharField(max_length=255, blank=True)
    language = models.ManyToManyField(Language, through='SiteLanguage', blank=True)
    geography = models.ManyToManyField(GeoZone, through='SiteGeoZone', blank=True)
    github_fork = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    course_type = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES, default='Unknown')
    registered_user_count = models.IntegerField(blank=True, null=True)
    active_learner_count = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.name + ' --- ' + self.url

    def get_languages(self):
        return ", ".join([l.name for l in self.language.all()])
    get_languages.short_description = "Languages"

    def get_geographies(self):
        return ", ".join([g.name for g in self.geography.all()])
    get_geographies.short_description = "Geographies"


class SiteGeoZone(models.Model):
    """
    Junction table for a site and GeoZones.
    """
    site = models.ForeignKey('Site', on_delete=models.CASCADE)
    geo_zone = models.ForeignKey('GeoZone', on_delete=models.CASCADE)
    # TODO: Add in attributes that describe the relationship between Site and GeoZone, and for history tracking

    def __unicode__(self):
        return self.site.pk + '-' + self.geo_zone.name


class SiteLanguage(models.Model):
    """
    Junction table for a site and Languages.
    """
    site = models.ForeignKey('Site', on_delete=models.CASCADE)
    language = models.ForeignKey('Language', on_delete=models.CASCADE)
    # TODO: Add in attributes that describe the relationship between Site and Language, and for history tracking

    def __unicode__(self):
        return self.site.pk + "-" + self.language.name
