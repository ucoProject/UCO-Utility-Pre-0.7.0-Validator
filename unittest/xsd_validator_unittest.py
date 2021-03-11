# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

import unittest
import rdflib
from rdflib.namespace import XSD
from xsd_validator import validate_xsd
from xsd_validator import XSDValidator, Singleton   # For internal state checks only
TOOL = rdflib.Namespace('https://unifiedcyberontology.org/ontology/uco/tool#')


class TestClassConstraints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_validate_xsd(self):

        # Singleton should be empty before doing any validations
        self.assertEqual(Singleton._instances, {})

        # Test with xsd_type URIRef
        errmsgs = validate_xsd('42', XSD.integer)
        print(errmsgs)
        self.assertEqual(len(errmsgs), 0)
        instance_id = id(XSDValidator)

        # Now check singleton
        self.assertEqual(set(Singleton._instances.keys()), {XSDValidator})
        self.assertIsInstance(Singleton._instances[XSDValidator], XSDValidator)

        # And check cache
        self.assertEqual(
            set(XSDValidator().xml_schema.keys()),
            {'xsd:integer', str(XSD.integer)})

        # Test another integer
        errmsgs = validate_xsd('42', 'xsd:integer')
        print(errmsgs)
        self.assertEqual(len(errmsgs), 0)

        # And check cache
        self.assertEqual(
            set(XSDValidator().xml_schema.keys()),
            {'xsd:integer', str(XSD.integer)})

        # Now check a boolean
        errmsgs = validate_xsd('false', 'xsd:boolean')
        print(errmsgs)
        self.assertEqual(len(errmsgs), 0)

        # And check cache
        self.assertEqual(
            set(XSDValidator().xml_schema.keys()),
            {'xsd:integer', 'xsd:boolean', str(XSD.integer), str(XSD.boolean)})

        # A bad integer
        errmsgs = validate_xsd('foo', XSD.integer)
        print(errmsgs)
        self.assertEqual(len(errmsgs), 1)

        # A bad boolean
        errmsgs = validate_xsd('4', 'xsd:boolean')
        print(errmsgs)
        self.assertEqual(len(errmsgs), 1)

        errmsgs = validate_xsd('', XSD.boolean)
        print(errmsgs)
        self.assertEqual(len(errmsgs), 1)

        # Check non-xsd type
        errmsgs = validate_xsd('4', TOOL.wrench)
        print(errmsgs)
        self.assertEqual(len(errmsgs), 1)

        # Check bad xsd type
        errmsgs = validate_xsd('4', XSD.wrench)
        print(errmsgs)
        self.assertEqual(len(errmsgs), 1)

        # Check bad xsd type again
        errmsgs = validate_xsd('4', XSD.wrench)
        print(errmsgs)
        self.assertEqual(len(errmsgs), 1)

        # Check singletonness
        self.assertEqual(instance_id, id(XSDValidator))

        # And check cache
        self.assertEqual(
            set(XSDValidator().xml_schema.keys()),
            {'xsd:integer', 'xsd:boolean', str(XSD.integer), str(XSD.boolean)})

if __name__ == '__main__':
    unittest.main()
