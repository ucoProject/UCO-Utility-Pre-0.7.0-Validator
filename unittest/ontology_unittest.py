# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

import os
import pprint
import unittest
import ontology
from property_constraints import PropertyConstraints
from class_constraints import ClassConstraints
import serializer
from rdflib import URIRef

class TestOntology(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
                                
    def setUp(self):
        self.this_dirpath = os.path.dirname(os.path.abspath(__file__))
        self.output_dirpath = os.path.join(self.this_dirpath, 'testdata', 'tmp')
        self.input_dirpath = os.path.join(self.this_dirpath, 'testdata', 'ontology')

    def tearDown(self):
        for filename in os.listdir(self.output_dirpath):
            os.remove(os.path.join(self.output_dirpath, filename))


    def test_full_ontology(self):
        o = ontology.get_ontology(os.path.join(self.input_dirpath, 'full_ontology'))

    def test_serialize(self):
        o = ontology.get_ontology(os.path.join(self.input_dirpath, 'tiny_ontology'))
        self.assertEqual(len(o.constraints), 18)

        serialized_filepath = os.path.join(self.output_dirpath, 'serialized.pkl')
        o.serialize(serialized_filepath, 'This is a test')

        o1 = ontology.get_ontology(serialized_filepath)
        self.assertEqual(len(o1.constraints), 18)

        with self.assertRaises(Exception):
            ontology.get_ontology(os.path.join(self.input_dirpath, 'tiny_ontology', 'README'))


    def test_net_constraints(self):
        c1 = URIRef('class1')
        c2 = URIRef('class2')
        c3 = URIRef('class3')
        c4 = URIRef('class4')
        c5 = URIRef('class5')
        p1 = URIRef('property1')
        p2 = URIRef('property2')
        p3 = URIRef('property3')
        r1 = URIRef('range1')
        r2 = URIRef('range2')

        def property_constraints(class_uri, property_uri, min_cardinality, max_cardinality, value_range):
            pc = PropertyConstraints(class_uri, property_uri)
            pc.min_cardinality = min_cardinality
            pc.max_cardinality = max_cardinality
            pc.value_range = value_range
            return pc

        parent_child_class_dict = {c1: [c2, c3, c4], c3: [c4, c5]}

        class_constraints1 = ClassConstraints(c1)
        class_constraints1.set_property_constraints(p1, property_constraints(c1, p1, None, 5, None))
        class_constraints1.set_property_constraints(p2, property_constraints(c1, p2, 0, 5, r1))

        class_constraints2 = ClassConstraints(c2)
        class_constraints2.set_property_constraints(p1, property_constraints(c2, p1, 3, 5, r1))
        class_constraints2.set_property_constraints(p3, property_constraints(c2, p3, 1, 2, r1))

        class_constraints3 = ClassConstraints(c3)
        class_constraints3.set_property_constraints(p2, property_constraints(c3, p2, 1, None, r1))

        class_constraints4 = ClassConstraints(c4)
        class_constraints4.set_property_constraints(p2, property_constraints(c4, p2, None, 7, r2))

        constraints = {
            c1: class_constraints1,
            c2: class_constraints2,
            c3: class_constraints3,
            c4: class_constraints4,
            c5: None
        }

        print('before...')
        pprint.pprint(parent_child_class_dict)
        pprint.pprint({k:str(v) for k, v in constraints.items()})
        net_constraints, errmsgs = ontology._inherit_constraints(constraints, parent_child_class_dict)
        print()
        print('after...')
        pprint.pprint({k:str(v) for k, v in net_constraints.items()})
        pprint.pprint(errmsgs)

        # expected values (computed by hand)
        self.maxDiff = None
        expected_class_constraints1 = ClassConstraints(c1)
        expected_class_constraints1.set_property_constraints(p1, property_constraints(c1, p1, None, 5, None))
        expected_class_constraints1.set_property_constraints(p2, property_constraints(c1, p2, 0,    5, r1))
        self.assertEqual(net_constraints[c1].property_constraints_dict, expected_class_constraints1.property_constraints_dict)

        expected_class_constraints2 = ClassConstraints(c2)
        expected_class_constraints2.set_property_constraints(p1, property_constraints(c2, p1, 3,    5, r1))
        expected_class_constraints2.set_property_constraints(p2, property_constraints(c2, p2, 0,    5, r1))
        expected_class_constraints2.set_property_constraints(p3, property_constraints(c2, p3, 1,    2, r1))
        self.assertEqual(net_constraints[c2].property_constraints_dict, expected_class_constraints2.property_constraints_dict)

        expected_class_constraints3 = ClassConstraints(c3)
        expected_class_constraints3.set_property_constraints(p1, property_constraints(c3, p1, None, 5, None))
        expected_class_constraints3.set_property_constraints(p2, property_constraints(c3, p2, 1,    5, r1))
        self.assertEqual(net_constraints[c3].property_constraints_dict, expected_class_constraints3.property_constraints_dict)

        expected_class_constraints4 = ClassConstraints(c4)
        expected_class_constraints4.set_property_constraints(p1, property_constraints(c4, p1, None, 5, None))
        expected_class_constraints4.set_property_constraints(p2, property_constraints(c4, p2, 0,    7, r2))
        self.assertEqual(net_constraints[c4].property_constraints_dict, expected_class_constraints4.property_constraints_dict)


    def test_get_property_ranges(self):
        ontospy_property_ranges = {
            URIRef('property1'): [URIRef('range1')],
            URIRef('property2'): [URIRef('range2a'), URIRef('range2b')],
            URIRef('property3'): []
        }
        ontospy_property_triples = {
            URIRef('property1'): [],
            URIRef('property2'): [],
            URIRef('property3'): []
        }
        property_ranges, errmsgs = ontology._get_property_ranges(
            ontospy_property_ranges, ontospy_property_triples)  # TODO: Stronger test
        expected_result = {
            URIRef('property1'): URIRef('range1'),
            URIRef('property2'): None,
            URIRef('property3'): None
        }
        pprint.pprint(errmsgs)
        self.assertEqual(property_ranges, expected_result)
        self.assertEqual(len(errmsgs), 2)


    def test_check_range_consistency(self):
        #TODO: Add subclass check

        def get_cc(class_uri, property_dict):
            class_constraints = ClassConstraints(class_uri)
            for property_uri, range_uri in property_dict.items():
                property_constraints = PropertyConstraints()
                property_constraints.value_range = URIRef(range_uri) if range_uri else None
                class_constraints.set_property_constraints(URIRef(property_uri), property_constraints)
            return class_constraints


        property_constraints = {
            URIRef('property1'): URIRef('range1'),
            URIRef('property2'): URIRef('range2'),
            URIRef('property3'): None
        }

        class_constraints = {
            URIRef('class1'): get_cc(URIRef('class1'), {'property1':'range1', 'property2':'range2'}),  # Both ok
            URIRef('class2'): get_cc(URIRef('class2'), {'property1':'range1'}),                        # OK
            URIRef('class3'): get_cc(URIRef('class3'), {'property1':'range2', 'property3':'range2'}),  # Bad range for property1, property3 ok
            URIRef('class4'): get_cc(URIRef('class4'), {'property1':'range2', 'property4':'range1'}),  # Property1 bad range, no such property4
            URIRef('class5'): get_cc(URIRef('class5'), {'property3':'range1', 'property4':'range1'}),  # Property3 ok, no such property4
            URIRef('class6'): get_cc(URIRef('class6'), {'property2':None, 'property3':None}),          # Both ok
            URIRef('class7'): 'Not a class constraint'         # Skip without error message
        }

        errmsgs = ontology._check_range_consistency(class_constraints, property_constraints)
        pprint.pprint(errmsgs)
        self.assertEqual(len(errmsgs), 4)


if __name__ == '__main__':
    unittest.main()
