from django.db import models

from txtalert.core.models import MSISDN


class Site(models.Model):
    uid = models.CharField(
        max_length=64, 
        unique=True,
        help_text="External partner system unique identifier."
    )
    title = models.CharField(
        max_length=64,
        help_text="Short descriptive site title."
    )


class ExternalUID(models.Model):
    uid = models.CharField(
        max_length=64,
        unique=True,
        help_text="External partner system unique identifier."
    )
    title = models.CharField(
        max_length=64,
        help_text="Short descriptive title of external partner system."
    )


class Patient(models.Model):
    hiv_status = models.CharField(
        max_length=16, 
        choices=(
            ('positive', 'positive'),
            ('negative', 'negative'),
            ('unknown', 'unknown'),
        ),
        help_text="Patient's Human Immunodeficiency Virus (HIV) status."
    )
    on_haart = models.BooleanField(
        help_text="Patient's Highly Active Antiretroviral Therapy (HAART) status. Ticked means the patient is activily receiving therapy."
    )
    msisdns = models.ManyToManyField(
        MSISDN, 
        related_name='pmtct_patient_set',
        help_text="Patient's contact numbers."
    )
    active_msisdn = models.ForeignKey(
        MSISDN,
        related_name="pmtct_active_msisdn_patient_set",
        verbose_name='Active phone number'
    )
    enroll_date = models.DateField(
        help_text="Date patient enrolled in study."
    )
    external_uids = models.ManyToManyField(
        ExternalUID,
        related_name='pmtct_patient_set',
        help_text="External partner system(s) unique identifiers."
    )
    sites = models.ManyToManyField(
        Site,
        help_text="Patient visit site(s) unique identifiers."
    )
    expected_delivery_date = models.DateField(
        help_text="Expected date of delivery."
    )
    haart_start_date = models.DateField(
        help_text="Date patient started full Highly Active Antiretroviral Therapy (HAART) treatment."
    )
    staged = models.BooleanField(
        help_text="Whether or not patient was staged at enrolment."
    )
    cd4_requested = models.BooleanField(
        help_text="Whether or not CD4 test was requested at enrolment."
    )
