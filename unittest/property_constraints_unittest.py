# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

import os
import pprint
import unittest
import rdflib
from property_constraints import PropertyConstraints


class TestPropertyConstraints(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cardinality_1(self):

        # Empty constraint
        constraint = PropertyConstraints(
            onto_class_uri = rdflib.term.URIRef('OntologyClass'),
            property_uri = rdflib.term.URIRef('OntologyProperty'))
        errmsgs = constraint.check_consistency()
        self.assertEqual(len(errmsgs), 0)

        # Add min_cardinality
        errmsgs = constraint.add_min_cardinality(1)
        self.assertEqual(constraint.min_cardinality, 1)
        self.assertIsNone(constraint.max_cardinality)
        self.assertFalse(constraint._qualified)
        self.assertEqual(len(errmsgs), 0)
        print(constraint.describe())

        # Add max_cardinality
        errmsgs = constraint.add_max_cardinality(5)
        self.assertEqual(constraint.min_cardinality, 1)
        self.assertEqual(constraint.max_cardinality, 5)
        self.assertFalse(constraint._qualified)
        self.assertEqual(len(errmsgs), 0)
        print(constraint.describe())

        # Duplicate add max_cardinality
        errmsgs = constraint.add_max_cardinality(5)
        self.assertEqual(constraint.min_cardinality, 1)
        self.assertEqual(constraint.max_cardinality, 5)
        self.assertFalse(constraint._qualified)
        self.assertEqual(len(errmsgs), 0)
        print(constraint.describe())

        # Add cardinality (fail)
        errmsgs = constraint.add_cardinality(3)
        self.assertEqual(constraint.min_cardinality, 1)
        self.assertEqual(constraint.max_cardinality, 5)
        self.assertFalse(constraint._qualified)
        self.assertEqual(len(errmsgs), 1)
        print(errmsgs)

        # Add qualified cardinality (fail)
        errmsgs = constraint.add_qualified_min_cardinality(1)
        self.assertEqual(constraint.min_cardinality, 1)
        self.assertEqual(constraint.max_cardinality, 5)
        self.assertFalse(constraint._qualified)
        self.assertEqual(len(errmsgs), 1)
        print(errmsgs)

        # Unqualified and no range
        errmsgs = constraint.check_consistency()
        self.assertEqual(len(errmsgs), 0)

        # Unqualified and value range (fail)
        errmsgs = constraint.add_value_range('foo')
        self.assertEqual(len(errmsgs), 0)
        errmsgs = constraint.check_consistency()
        self.assertEqual(len(errmsgs), 1)
        print(errmsgs)


    def test_cardinality_2(self):

        # Empty contraint
        constraint = PropertyConstraints(
            onto_class_uri = rdflib.term.URIRef('OntologyClass'),
            property_uri = rdflib.term.URIRef('OntologyProperty'))
        errmsgs = constraint.check_consistency()
        self.assertEqual(len(errmsgs), 0)

        # Add qualified_min_cardinality
        errmsgs = constraint.add_qualified_min_cardinality(1)
        self.assertEqual(constraint.min_cardinality, 1)
        self.assertIsNone(constraint.max_cardinality)
        self.assertTrue(constraint._qualified)
        self.assertEqual(len(errmsgs), 0)
        print(constraint.describe())

        # Add qualified_max_cardinality too small (fail)
        errmsgs = constraint.add_qualified_max_cardinality(0)
        self.assertEqual(constraint.min_cardinality, 1)
        self.assertIsNone(constraint.max_cardinality)
        self.assertTrue(constraint._qualified)
        self.assertEqual(len(errmsgs), 1)
        print(errmsgs)

        # Add qualified cardinality (fail)
        errmsgs = constraint.add_qualified_cardinality(3)
        self.assertEqual(constraint.min_cardinality, 1)
        self.assertIsNone(constraint.max_cardinality)
        self.assertTrue(constraint._qualified)
        self.assertEqual(len(errmsgs), 1)
        print(errmsgs)

        # Add unqualified cardinality (fail)
        errmsgs = constraint.add_cardinality(3)
        self.assertEqual(constraint.min_cardinality, 1)
        self.assertIsNone(constraint.max_cardinality)
        self.assertTrue(constraint._qualified)
        self.assertEqual(len(errmsgs), 2)
        print(errmsgs)

        # Qualified and no range (fail)
        errmsgs = constraint.check_consistency()
        self.assertEqual(len(errmsgs), 1)
        print(errmsgs)


        # Qualified and value range
        errmsgs = constraint.add_value_range('foo')
        errmsgs = constraint.check_consistency()
        self.assertEqual(len(errmsgs), 0)

        # Add value range too (fail)
        errmsgs = constraint.add_value_range('bar')
        self.assertEqual(len(errmsgs), 1)
        print(errmsgs)


    def test_cardinality_3(self):

        # Empty contraint
        constraint = PropertyConstraints(
            onto_class_uri = rdflib.term.URIRef('OntologyClass'),
            property_uri = rdflib.term.URIRef('OntologyProperty'))
        errmsgs = constraint.check_consistency()
        self.assertEqual(len(errmsgs), 0)

        # Forbidden value
        errmsgs = constraint.add_qualified_cardinality(0)
        self.assertEqual(constraint.min_cardinality, 0)
        self.assertEqual(constraint.max_cardinality, 0)
        print(constraint.describe())
        
        # Forbidden value range
        errmsgs = constraint.add_value_range('foo')
        print(constraint.describe())


    def test_equality(self):
        constraint1 = PropertyConstraints(
            onto_class_uri = rdflib.term.URIRef('OntologyClass'),
            property_uri = rdflib.term.URIRef('OntologyProperty'))
        constraint1.add_qualified_min_cardinality(3)
        constraint1.add_qualified_max_cardinality(7)
        constraint1.add_value_range('bar')

        constraint2 = PropertyConstraints(
            onto_class_uri = rdflib.term.URIRef('OntologyClass'),
            property_uri = rdflib.term.URIRef('OntologyProperty'))
        constraint2.add_qualified_min_cardinality(3)
        constraint2.add_qualified_max_cardinality(7)
        constraint2.add_value_range('bar')

        self.assertEqual(constraint1, constraint1)
        self.assertEqual(constraint1, constraint2)

        constraint2.max_cardinality = 4
        self.assertNotEqual(constraint1, constraint2)
        

    def test_merge_cardinality(self):
        parent = PropertyConstraints(
            onto_class_uri = rdflib.term.URIRef('ParentClass'),
            property_uri = rdflib.term.URIRef('OntologyProperty'))
        child = PropertyConstraints(
            onto_class_uri = rdflib.term.URIRef('ChildClass'),
            property_uri = rdflib.term.URIRef('OntologyProperty'))

        def cardtest(t1, t2, t3, n):
            child.min_cardinality, child.max_cardinality = t1
            parent.min_cardinality, parent.max_cardinality = t2
            merged, errmsgs = child.merge_parent(parent)
            if errmsgs:
                pprint.pprint(errmsgs)
            self.assertEqual((merged.min_cardinality, merged.max_cardinality), t3)
            self.assertEqual(len(errmsgs), n)
            if t1 == t3:
                self.assertEqual(merged, child)


        # Unset child inherits parent's attributes with no errors
        cardtest( (None, None), (None, None), (None, None), 0)
        cardtest( (None, None), (None, 2),    (None, 2),    0)
        cardtest( (None, None), (1, None),    (1, None),    0)
        cardtest( (None, None), (1, 2),       (1, 2),       0)

        # Child with unset min and specified max gets parent's min, keeps its max, and may set error
        cardtest( (None, 3), (None, None), (None, 3), 0)   # child ignores parent with no constraints
        cardtest( (None, 3), (1, 4),       (1, 3),    0)   # child's constraint is a subset of parent's
        cardtest( (None, 3), (2, 3),       (2, 3),    0)   # child's constraint is same as parent's
        cardtest( (None, 3), (2, 2),       (2, 3),    1)   # child's constraint not a subset of parent's
        cardtest( (None, 3), (9, None),    (None, 3), 1)   # parent's constraint rejected because min>max
        cardtest( (None, 3), (9, 2),       (None, 3), 2)   # parent's constraint too tight and then rejected min>max

        # Child with unset max and specified min gets parent's max, keeps its min, and may set error
        cardtest( (3, None), (None, None), (3, None), 0)   # child ignores parent with no constraints
        cardtest( (3, None), (2, None),    (3, None), 0)   # child's constraint is a subset of parent's
        cardtest( (3, None), (3, None),    (3, None), 0)   # child's constraint is same as parent's
        cardtest( (3, None), (4, None),    (3, None), 1)   # child's constraint not a subset of parent's
        cardtest( (3, None), (None, 1),    (3, None), 1)   # parent's constraint rejected because min>max

        # Child with both min and max values never changes, but may have errors
        cardtest( (2, 4), (None, None), (2, 4), 0)   # child ignores parent with no constraints
        cardtest( (2, 4), (1, None),    (2, 4), 0)   # child's min constraint tighter than parent's
        cardtest( (2, 4), (2, None),    (2, 4), 0)   # parent's min constraint same as child's
        cardtest( (2, 4), (3, None),    (2, 4), 1)   # parent's min constraint tighter than child's
        cardtest( (2, 4), (None, 5),    (2, 4), 0)   # child's max constraint tighter than parent's
        cardtest( (2, 4), (None, 4),    (2, 4), 0)   # parent's max constraint same as child's
        cardtest( (2, 4), (None, 3),    (2, 4), 1)   # parent's max constraint tighter than child's
        cardtest( (2, 4), (1, 5), (2, 4), 0)   # child's constraint is a subset of parent's
        cardtest( (2, 4), (2, 4), (2, 4), 0)   # child's constraint is same as parent's
        cardtest( (2, 4), (3, 4), (2, 4), 1)   # child's constraint not a subset of parent's
        cardtest( (2, 4), (3, 3), (2, 4), 2)   # child's constraint not a subset of parent's
        cardtest( (2, 4), (7, 9), (2, 4), 1)   # child's constraint not a subset of parent's


    def test_merge_range(self):
        parent = PropertyConstraints(
            onto_class_uri = rdflib.term.URIRef('ParentClass'),
            property_uri = rdflib.term.URIRef('OntologyProperty'))
        child = PropertyConstraints(
            onto_class_uri = rdflib.term.URIRef('ChildClass'),
            property_uri = rdflib.term.URIRef('OntologyProperty'))

        def rangetest(r1, r2, r3, n):
            child.value_range = r1
            parent.value_range = r2
            merged, errmsgs = child.merge_parent(parent)
            if errmsgs:
                pprint.pprint(errmsgs)
            self.assertEqual(merged.value_range, r3)
            self.assertEqual(len(errmsgs), n)
            if r1 == r3:
                self.assertEqual(merged, child)

        # Unset child inherts parent range with no errors
        rangetest( None, None,  None,  0)
        rangetest( None, 'foo', 'foo', 0)

        # Child with range keeps its value but has error if parent's range is not a superclass of child's
        # At this point, range class hierarchy is not implemented, so we raise error if ranges differ
        rangetest( 'foo', 'foo',  'foo',  0)
        rangetest( 'foo', 'bar',  'foo',  1)




if __name__ == '__main__':
    unittest.main()
