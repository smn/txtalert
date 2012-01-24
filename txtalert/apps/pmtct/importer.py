import logging
import urllib2

import socks
from suds.client import Client

logger = logging.getLogger(__name__)

def proxy_wrapper(f):
    """
    Causes decorated methods to forward urllib2 requests through SSH created SOCKS5 proxy on 127.0.0.1:8080.
    Create a SOCK5 proxy locally like so: $ ssh -ND 8080 <user>@<host>
    """
    def wrapper(self, *args, **kwargs):
        if self.proxy:
            orig_socket = urllib2.socket.socket
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 8080)
            # Monkeypath urllib2 module to use proxied socket.
            socks.wrapmodule(urllib2)
            try:
                result = f(self, *args, **kwargs)
            except Exception, e:
                # Restore original urllib2 socket.
                urllib2.socket.socket = orig_socket
                raise
            finally:
                urllib2.socket.socket = orig_socket
        else:
            result = f(self, *args, **kwargs)
        return result
    return wrapper

class Importer(object):

    def __init__(self, uri='http://bookwise.kznhealth.gov.za/Main.asmx?wsdl', proxy=False, verbose=False):
        self.proxy = proxy
        self._init_client(uri=uri)
    
    def _dictify_data(self, data):
        """
        Convert per field structured data to dictionary list.
        I.e. 
        {
            'field1': ['obj0.field1', 'obj1.field1', 'obj2.field1'],
            'field2': ['obj0.field2', 'obj1.field2', 'obj2.field2'],
            'field3': ['obj0.field3', 'obj1.field3', 'obj2.field3'],
        }
        to
        [
            {'field1': 'obj0.field1', 'field2': 'obj0.field2', 'field3': 'obj0.field3'},
            {'field1': 'obj1.field1', 'field2': 'obj1.field2', 'field3': 'obj1.field3'},
            {'field1': 'obj2.field1', 'field2': 'obj2.field2', 'field3': 'obj2.field3'},
        ]
        """
        objs = []
        for key, value in dict(data).items():
            for i, x in enumerate(value):
                try:
                    obj = objs[i]
                except IndexError:
                    obj = {}
                    objs.append(obj)
                obj[key] = x
        return objs

    @proxy_wrapper
    def _init_client(self, uri):
        """
        Initiates SOAP client.
        There are two ports, "Service1Soap" and "Service1Soap12" which appear to mirror of each other.
        """
        self.client = Client(uri)
        self.client.set_options(service='Service1', port="Service1Soap")

    @proxy_wrapper
    def _call_method(self, method, site_code=None, new=True):
        """
        Returns dictified result for method call.
        Returns combined results for all site codes if no site code provided.
        With new=True return only new entries since last run.
        With new=False returns all entries.
        """
        SITE_CODES = [
            'EDH',
            'MSH',
        ]

        if not site_code:
            result = []
            for site_code in SITE_CODES:
                response = getattr(self.client.service, method)(crit='critNEW' if new else 'critALL', siteCode=site_code)
                result += self._dictify_data(response['DataRoot']['Data'])
        else:
            response = getattr(self.client.service, method)(crit='critNEW' if new else 'critALL', siteCode=site_code)
            result = self._dictify_data(response['DataRoot']['Data'])

        return result


    def get_delivery_triggers(self, site_code, new=True):
        """
        Returns delivery triggers for all enrolled patients
        or only those enrolled since last run(new).
        """
        data = self._call_method(
            method='I_DeliveryTrigger', 
            site_code=site_code,
            new=new
        )
    
    def get_enrolled_patients(self, site_code=None, new=True):
        """
        Returns all enrolled patients or only those enrolled
        since last run(new).
        """
        return self._call_method(
            method='I_PatientEnrollment', 
            site_code=site_code,
            new=new
        )
    
    def get_post_natal_triggers(self, site_code, new=True):
        """
        Returns post natal triggers for all enrolled patients
        or only those enrolled since last run(new).
        """
        data = self._call_method(
            method='I_PostNatalTrigger',
            site_code=site_code,
            new=new
        )

    def get_pre_natal_triggers(self, site_code, new=True):
        """
        Returns pre natal triggers for all enrolled patients
        or only those enrolled since last run(new).
        """
        data = self._call_method(
            method='I_PreNatalTrigger', 
            site_code=site_code,
            new=new
        )

    def update_patients(self):
        patients = self.get_enrolled_patients(new=False)
