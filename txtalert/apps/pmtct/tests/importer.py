from unittest import TestCase
from txtalert.apps.pmtct.importer import Importer

class ImporterTestCase(TestCase):

    def setUp(self):
        self.importer = Importer(proxy=True)

    def test_dictify_data(self):
        test_data = {
            'field1': ['obj0.field1', 'obj1.field1', 'obj2.field1'],
            'field2': ['obj0.field2', 'obj1.field2', 'obj2.field2'],
            'field3': ['obj0.field3', 'obj1.field3', 'obj2.field3'],
        }

        data = self.importer._dictify_data(test_data)

        for i, obj in enumerate(data):
            for j in range(1, 4):
                self.failUnlessEqual(obj['field%s' % j], 'obj%s.field%s' % (i, j))
    
    def test_get_delivery_triggers(self):
        self.failUnless(self.importer.get_delivery_triggers())

    def test_get_enrolled_patients(self):
        self.failUnless(self.importer.get_enrolled_patients())
    
    def test_get_post_natal_triggers(self):
        self.failUnless(self.importer.get_post_natal_triggers())
    
    def test_get_pre_natal_triggers(self):
        self.failUnless(self.importer.get_pre_natal_triggers())
    
