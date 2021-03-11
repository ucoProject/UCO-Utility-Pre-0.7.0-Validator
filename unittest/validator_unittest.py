# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

import json
import os
import pprint
import unittest
import message
from casedata import get_casedata, CaseData
from ontology import get_ontology, Ontology
import validator
from class_constraints import ClassConstraints
from property_constraints import PropertyConstraints
from rdflib import URIRef, Literal, BNode
from rdflib.namespace import XSD, RDF
from datatype_constraints import VocabularyDatatypeConstraints

class TestValidator(unittest.TestCase):

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

    def test_validate_literals(self):

        # A Vocabulary Datatype
        stooges_uri = URIRef('http://example.com/test#Stooges')
        stooges_datatype = VocabularyDatatypeConstraints(stooges_uri, {})
        stooges_datatype.vocabulary = {'Moe', 'Larry', 'Curley'}

        # An unknown Datatype
        unknown_uri = URIRef('http://example.com/test#Unknown')

        # ontology.constraints contains the Vocabulary Datatype but not the unknown one
        ontology_constraints = {
            stooges_uri: stooges_datatype
        }

        # A collection of values
        values = [
            Literal('hello'),                              # No datatype implies XSD.string
            Literal('12345', datatype=XSD.integer),        # A good integer
            Literal('bad_integer', datatype=XSD.integer),  # A bad integer -- ERROR
            Literal('Moe', datatype=stooges_uri),          # A good Datatype
            Literal('Jack', datatype=stooges_uri),         # A bad Datatype -- ERROR
            Literal('Who?', datatype=unknown_uri),         # An unknown Datatype -- ERROR
            Literal('What?', datatype='foo')               # A Datatype that isn't even a URIRef -- ERROR
        ]

        # Validate the values
        errmsgs = validator.validate_literals(values, ontology_constraints)
        pprint.pprint(errmsgs)
        self.assertEqual(len(errmsgs), 4)


    def test_validate_cardinality_constraints(self):

        # Define URIs
        property1_uri = URIRef('property1')
        property2_uri = URIRef('property2')
        property3_uri = URIRef('property3')
        property4_uri = URIRef('property4')
        property5_uri = URIRef('property5')

        # Build ClassConstraints
        class_constraints = ClassConstraints('my_class')

        property1_constraints = PropertyConstraints()
        property1_constraints.min_cardinality = None
        property1_constraints.max_cardinality = None
        class_constraints.set_property_constraints(property1_uri, property1_constraints)   # No cardinality constraint

        property2_constraints = PropertyConstraints()
        property2_constraints.min_cardinality = None
        property2_constraints.max_cardinality = 1
        class_constraints.set_property_constraints(property2_uri, property2_constraints)   # At most 1 value

        property3_constraints = PropertyConstraints()
        property3_constraints.min_cardinality = 1
        property3_constraints.max_cardinality = 2
        class_constraints.set_property_constraints(property3_uri, property3_constraints)   # 1 or 2 values

        property4_constraints = PropertyConstraints()
        property4_constraints.min_cardinality = 2
        property4_constraints.max_cardinality = 3
        class_constraints.set_property_constraints(property4_uri, property4_constraints)   # 2 or 3 values

        property5_constraints = PropertyConstraints()
        property5_constraints.min_cardinality = 1
        property5_constraints.max_cardinality = None
        class_constraints.set_property_constraints(property5_uri, property5_constraints)   # REQUIRED, at least 1 value

        # Build data values
        pvt_dict = {
            property1_uri: {'value1a':'type1', 'value1b':'type1'},   # OK
            property2_uri: {'value2a':'type2', 'value2b':'type2'},   # ERROR: Violates constraint
            property3_uri: {'value3a':'type3', 'value3b':'type3'},   # OK
            property4_uri: {'value4a':'type4', 'value4b':'type4'}    # OK
        }                                                            # ERROR: property5 is REQUIRED

        # Validate
        errmsgs = validator.validate_cardinality_constraints(pvt_dict, class_constraints)
        self.assertEqual(len(errmsgs), 2)
        pprint.pprint(errmsgs)

    def test_validate_range_constraints(self):

        # ontology  ClassConstraint   Value         Outcome with CC     Outcome without CC
        #    t0          t0           CONFLICT      ERROR               ERROR
        #    t1          t1           t1            OK                  OK
        #    x           t2           t2            OK                  ERROR
        #    -           t3           t3            OK                  OK
        #    t4          x            t4            ERROR               OK
        #    x           x            t5            ERROR               ERROR
        #    -           x            t6            ERROR               OK
        #    t7          -            t7            OK                  OK
        #    x           -            t8            ERROR               ERROR
        #    -           -            t9            OK                  OK

        # Build URIs
        property_uris = [URIRef('property{}'.format(n)) for n in range(12)]
        type_uris = [URIRef('type{}'.format(n)) for n in range(12)]
        wrong_type_uri = URIRef('wrong_type')

        def get_pc(value_type):
            property_constraints = PropertyConstraints()
            property_constraints.value_range = value_type
            return property_constraints

        # Build ClassConstraints
        class_constraints = ClassConstraints('my_class')
        class_constraints.set_property_constraints(property_uris[0], get_pc(type_uris[0]))
        class_constraints.set_property_constraints(property_uris[1], get_pc(type_uris[1]))
        class_constraints.set_property_constraints(property_uris[2], get_pc(type_uris[2]))
        class_constraints.set_property_constraints(property_uris[3], get_pc(type_uris[3]))
        class_constraints.set_property_constraints(property_uris[4], get_pc(wrong_type_uri))
        class_constraints.set_property_constraints(property_uris[5], get_pc(wrong_type_uri))
        class_constraints.set_property_constraints(property_uris[6], get_pc(wrong_type_uri))

        # Build ontology property ranges
        ontology_property_ranges = {
            property_uris[0]:type_uris[0],
            property_uris[1]:type_uris[1],
            property_uris[2]:wrong_type_uri,
            property_uris[4]:type_uris[4],
            property_uris[5]:wrong_type_uri,
            property_uris[7]:type_uris[7],
            property_uris[8]:wrong_type_uri
        }

        # Build data values
        pvt_dict = {
            property_uris[0]: {'value0a':type_uris[0], 'value0b':wrong_type_uri},
            property_uris[1]: {'value1':type_uris[1]},
            property_uris[2]: {'value1':type_uris[2]},
            property_uris[3]: {'value1':type_uris[3]},
            property_uris[4]: {'value1':type_uris[4]},
            property_uris[5]: {'value1':type_uris[5]},
            property_uris[6]: {'value1':type_uris[6]},
            property_uris[7]: {'value1':type_uris[7]},
            property_uris[8]: {'value1':type_uris[8]},
            property_uris[9]: {'value1':type_uris[9]},
        }

        # Test without CC
        errmsgs = validator.validate_range_constraints(pvt_dict, ontology_property_ranges)
        pprint.pprint(errmsgs)
        print
        self.assertEqual(len(errmsgs), 4)  # Errors on 0, 2, 5, 8

        # Test with CC
        errmsgs = validator.validate_range_constraints(pvt_dict, ontology_property_ranges, class_constraints)
        pprint.pprint(errmsgs)
        self.assertEqual(len(errmsgs), 5)  # Errors on 0, 4, 5, 6, 8

        
    def test_get_value_type_literal(self):

        datatype, errmsgs = validator.get_value_type(Literal('foo'), None)  # Default datatype is xsd:string
        self.assertEqual(datatype, XSD.string)
        self.assertEqual(len(errmsgs), 0)

        datatype, errmsgs = validator.get_value_type(Literal('123', datatype=XSD.integer), None)
        self.assertEqual(datatype, XSD.integer)
        self.assertEqual(len(errmsgs), 0)

        datatype, errmsgs = validator.get_value_type(Literal('123', datatype=URIRef('xsd:integer')), None)
        self.assertEqual(datatype, XSD.integer)
        self.assertEqual(len(errmsgs), 0)

        datatype, errmsgs = validator.get_value_type(Literal('123', datatype=URIRef('xsd:integer')), None)
        self.assertEqual(datatype, XSD.integer)
        self.assertEqual(len(errmsgs), 0)

        datatype, errmsgs = validator.get_value_type(Literal('123', datatype=URIRef('integer')), None)
        pprint.pprint(errmsgs)
        self.assertEqual(datatype, None)
        self.assertEqual(len(errmsgs), 1)

        datatype, errmsgs = validator.get_value_type(Literal('123', datatype=URIRef('foo:bar:integer')), None)
        pprint.pprint(errmsgs)
        self.assertEqual(datatype, None)
        self.assertEqual(len(errmsgs), 1)


    def test_get_value_type_link(self):

        spo_dict = {
            URIRef('subject1'): {RDF.type: {URIRef('subject2')}},
            URIRef('subject2'): {RDF.type: {BNode('subject3')}},
            BNode('subject3'): {RDF.type: {URIRef('subject2')}},
            BNode('bad_subject1'): {RDF.type: {URIRef('subject2'), URIRef('subject3')}},
            BNode('bad_subject2'): {RDF.type: set()},
            BNode('bad_subject3'): {}
        }

        datatype, errmsgs = validator.get_value_type(URIRef('subject1'), spo_dict)   # Expect URIRef('subject2')
        self.assertEqual(datatype, URIRef('subject2'))
        self.assertEqual(len(errmsgs), 0)

        datatype, errmsgs = validator.get_value_type(BNode('subject3'), spo_dict)   # Expect URIRef('subject2')
        self.assertEqual(datatype, URIRef('subject2'))
        self.assertEqual(len(errmsgs), 0)

        datatype, errmsgs = validator.get_value_type(BNode('bad_subject1'), spo_dict)   # Expect ERROR
        pprint.pprint(errmsgs)
        self.assertEqual(datatype, None)
        self.assertEqual(len(errmsgs), 1)

        datatype, errmsgs = validator.get_value_type(BNode('bad_subject2'), spo_dict)   # Expect ERROR
        pprint.pprint(errmsgs)
        self.assertEqual(datatype, None)
        self.assertEqual(len(errmsgs), 1)

        datatype, errmsgs = validator.get_value_type(BNode('bad_subject3'), spo_dict)   # Expect ERROR
        pprint.pprint(errmsgs)
        self.assertEqual(datatype, None)
        self.assertEqual(len(errmsgs), 1)

        datatype, errmsgs = validator.get_value_type(BNode('missing_subject'), spo_dict)   # Expect ERROR
        pprint.pprint(errmsgs)
        self.assertEqual(datatype, None)
        self.assertEqual(len(errmsgs), 1)


    def test_validate_case_data(self):
        pass

    def test_validator(self):
        case_data = get_casedata('../data/samples-0.4/Oresteia.json')
        ontology = get_ontology('../data/ontology-0.4.0/ontology.pkl')
        #case_data = get_casedata('../data/samples-0.4/Oresteia.pkl')
        #ontology = get_ontology('../data/ontology-0.5.0-0.2.0/ontology.pkl')
        #ontology = get_ontology('../data/ontology-0.4.0/ontology.pkl')
        pprint.pprint(ontology.error_messages)
        error_messages = validator.validate(ontology, case_data)
        print()
        print('Final error messages')
        pprint.pprint(error_messages)

if __name__ == '__main__':
    unittest.main()
