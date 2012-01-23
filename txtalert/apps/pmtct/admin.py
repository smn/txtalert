from django.contrib import admin

from txtalert.apps.pmtct.models import ExternalUID, Patient, Site

admin.site.register(ExternalUID)
admin.site.register(Patient)
admin.site.register(Site)
