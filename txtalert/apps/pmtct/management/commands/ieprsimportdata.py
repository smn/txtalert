from optparse import make_option

from django.conf import settings 
from django.core.management.base import BaseCommand

from txtalert.apps.pmtct.importer import Importer

class Command(BaseCommand):
    help = "Can be run as a cronjob or directly to import IePRS data."
    option_list = BaseCommand.option_list + (
        make_option('--proxy', 
            action='store_true', 
            dest='proxy',
            default=False,
            help='Proxy requests through SSH tunnel (run $ ssh -fND 8080 <user>@<host>)'),
        )
    
    def handle(self, proxy, *args, **kwargs):
        importer = Importer(
            proxy=proxy,
            verbose=settings.DEBUG,
        )

        importer.get_enrolled_patients(site_code="EDH")
