# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

import unittest
import rdflib
from rdflib.namespace import XSD
from class_constraints import get_class_constraints
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

    def test_single_bnode(self):
        '''
        <Class *https://unifiedcyberontology.org/ontology/uco/tool#BuildConfigurationType*>
        '''
        triples = [
            (rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#BuildConfigurationType'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Class')),
            (rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#BuildConfigurationType'),
             rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'),
             rdflib.term.BNode('ub3bL40C18')),
            (rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#BuildConfigurationType'),
             rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#comment'),
             rdflib.term.Literal('Describes how the build utility was configured for a particular build of a particular software.', lang='en')),
            (rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#BuildConfigurationType'),
             rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'),
             rdflib.term.Literal('BuildConfigurationType', lang='en')),
            (rdflib.term.BNode('ub3bL40C18'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#maxQualifiedCardinality'),
             rdflib.term.Literal('1', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
            (rdflib.term.BNode('ub3bL40C18'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
             rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
            (rdflib.term.BNode('ub3bL40C18'),  # Duplicate conflicting
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
             rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer')),
            (rdflib.term.BNode('ub3bL40C18'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#configurationSettingDescription')),
            (rdflib.term.BNode('ub3bL40C18'),  # Duplicate not conflicting
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#configurationSettingDescription')),
            (rdflib.term.BNode('ub3bL40C18'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction'))
        ]
        class_constraints, errmsgs = get_class_constraints(
           onto_class_uri = rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#BuildConfigurationType'),
           triples = triples)
        print(class_constraints.describe())
        print(errmsgs)
        self.assertEqual(len(errmsgs), 2)  # duplicate, missing range (because duplicate range removed)
        property_constraints = class_constraints.property_constraints_dict[TOOL.configurationSettingDescription]
        self.assertEqual(property_constraints.onto_class_uri, 
                         rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#BuildConfigurationType'))
        self.assertEqual(property_constraints.property_uri, TOOL.configurationSettingDescription)
        self.assertEqual(property_constraints.min_cardinality, None)
        self.assertEqual(property_constraints.max_cardinality, 1)
        self.assertEqual(property_constraints.value_range, None)   # conflicting specifications removed
        self.assertEqual(property_constraints._qualified, True)


    def test_min_and_max_required(self):
        '''
        TOOL.buildOutputLog: MIN AND MAX REQUIRED
        '''
        triples = [
            (rdflib.term.BNode('ub3bL82C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#minQualifiedCardinality'),
             rdflib.term.Literal('1', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
            (rdflib.term.BNode('ub3bL82C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#maxQualifiedCardinality'),
             rdflib.term.Literal('4', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
            (rdflib.term.BNode('ub3bL82C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
             rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
            (rdflib.term.BNode('ub3bL82C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#buildOutputLog')),
            (rdflib.term.BNode('ub3bL82C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction'))
        ]
        class_constraints, errmsgs = get_class_constraints(rdflib.term.URIRef('foo8'), triples)
        print(class_constraints.describe())
        self.assertEqual(len(errmsgs), 0)
        property_constraints = class_constraints.property_constraints_dict[TOOL.buildOutputLog]
        self.assertEqual(property_constraints.onto_class_uri, rdflib.term.URIRef('foo8'))
        self.assertEqual(property_constraints.property_uri, TOOL.buildOutputLog)
        self.assertEqual(property_constraints.min_cardinality, 1)
        self.assertEqual(property_constraints.max_cardinality, 4)
        self.assertEqual(property_constraints.value_range, XSD.string)
        self.assertEqual(property_constraints._qualified, True)
        self.assertEqual(class_constraints.get_required_properties(), {TOOL.buildOutputLog})

    def test_min_only_required(self):
        '''
        TOOL.buildVersion:  MIN ONLY, REQUIRED
        '''
        triples = [
            (rdflib.term.BNode('ub3bL100C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
             rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
            (rdflib.term.BNode('ub3bL100C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#minQualifiedCardinality'),
             rdflib.term.Literal('1', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
            (rdflib.term.BNode('ub3bL100C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#buildVersion')),
            (rdflib.term.BNode('ub3bL100C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction')),
        ]
        class_constraints, errmsgs = get_class_constraints(rdflib.term.URIRef('foo7'), triples)
        print(class_constraints.describe())
        self.assertEqual(len(errmsgs), 0)
        property_constraints = class_constraints.property_constraints_dict[TOOL.buildVersion]
        self.assertEqual(property_constraints.onto_class_uri, rdflib.term.URIRef('foo7'))
        self.assertEqual(property_constraints.property_uri, TOOL.buildVersion)
        self.assertEqual(property_constraints.min_cardinality, 1)
        self.assertEqual(property_constraints.max_cardinality, None)
        self.assertEqual(property_constraints.value_range, XSD.string)
        self.assertEqual(property_constraints._qualified, True)
        self.assertEqual(class_constraints.get_required_properties(), {TOOL.buildVersion})

    def test_max_only(self):
        '''
        TOOL.buildUtility:  MAX ONLY
        TOOL.buildConfiguration:  MAX ONLY
        TOOL.buildLabel:  MAX ONLY
        '''
        triples = [
            (rdflib.term.BNode('ub3bL64C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onClass'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#BuildUtilityType')),
            (rdflib.term.BNode('ub3bL64C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#maxQualifiedCardinality'),
             rdflib.term.Literal('1', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
            (rdflib.term.BNode('ub3bL64C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction')),
            (rdflib.term.BNode('ub3bL64C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#buildUtility')),
            (rdflib.term.BNode('ub3bL58C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#maxQualifiedCardinality'),
             rdflib.term.Literal('1', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
            (rdflib.term.BNode('ub3bL58C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onClass'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#BuildConfigurationType')),
            (rdflib.term.BNode('ub3bL58C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction')),
            (rdflib.term.BNode('ub3bL58C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#buildConfiguration')),
            (rdflib.term.BNode('ub3bL76C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#buildLabel')),
            (rdflib.term.BNode('ub3bL76C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#maxQualifiedCardinality'),
             rdflib.term.Literal('1', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
            (rdflib.term.BNode('ub3bL76C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
             rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
            (rdflib.term.BNode('ub3bL76C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction')),
        ]
        class_constraints, errmsgs = get_class_constraints(rdflib.term.URIRef('foo1'), triples)
        print(class_constraints.describe())
        self.assertEqual(len(class_constraints.property_constraints_dict), 3)
        self.assertEqual(len(errmsgs), 0)
        property_constraints = class_constraints.property_constraints_dict[TOOL.buildUtility]
        self.assertEqual(property_constraints.onto_class_uri, rdflib.term.URIRef('foo1'))
        self.assertEqual(property_constraints.property_uri, TOOL.buildUtility)
        self.assertEqual(property_constraints.min_cardinality, None)
        self.assertEqual(property_constraints.max_cardinality, 1)
        self.assertEqual(property_constraints.value_range, TOOL.BuildUtilityType)
        self.assertEqual(property_constraints._qualified, True)
        property_constraints = class_constraints.property_constraints_dict[TOOL.buildConfiguration]
        self.assertEqual(property_constraints.onto_class_uri, rdflib.term.URIRef('foo1'))
        self.assertEqual(property_constraints.property_uri, TOOL.buildConfiguration)
        self.assertEqual(property_constraints.min_cardinality, None)
        self.assertEqual(property_constraints.max_cardinality, 1)
        self.assertEqual(property_constraints.value_range, TOOL.BuildConfigurationType)
        self.assertEqual(property_constraints._qualified, True)
        property_constraints = class_constraints.property_constraints_dict[TOOL.buildLabel]
        self.assertEqual(property_constraints.onto_class_uri, rdflib.term.URIRef('foo1'))
        self.assertEqual(property_constraints.property_uri, TOOL.buildLabel)
        self.assertEqual(property_constraints.min_cardinality, None)
        self.assertEqual(property_constraints.max_cardinality, 1)
        self.assertEqual(property_constraints.value_range, XSD.string)
        self.assertEqual(property_constraints._qualified, True)


    def test_forbidden(self):
        '''
        TOOL.buildID:  FORBIDDEN
        '''
        triples = [
            (rdflib.term.BNode('ub3bL70C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#buildID')),
            (rdflib.term.BNode('ub3bL70C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction')),
            (rdflib.term.BNode('ub3bL70C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
             rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
            (rdflib.term.BNode('ub3bL70C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#maxQualifiedCardinality'),
             rdflib.term.Literal('0', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
        ]
        class_constraints, errmsgs = get_class_constraints(rdflib.term.URIRef('foo6'), triples)
        print(class_constraints.describe())
        self.assertEqual(len(errmsgs), 0)
        property_constraints = class_constraints.property_constraints_dict[TOOL.buildID]
        self.assertEqual(property_constraints.onto_class_uri, rdflib.term.URIRef('foo6'))
        self.assertEqual(property_constraints.property_uri, TOOL.buildID)
        self.assertEqual(property_constraints.min_cardinality, None)
        self.assertEqual(property_constraints.max_cardinality, 0)
        self.assertEqual(property_constraints.value_range, XSD.string)
        self.assertEqual(property_constraints._qualified, True)
        self.assertEqual(class_constraints.get_forbidden_properties(), {TOOL.buildID})



    def test_no_cardinality_no_range(self):
        '''
        TOOL.buildProject:  NO CARDINALITY NO RANGE
        '''
        triples = [
            (rdflib.term.BNode('ub3bL88C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#buildProject')),
            (rdflib.term.BNode('ub3bL88C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction')),
        ]
        class_constraints, errmsgs = get_class_constraints(rdflib.term.URIRef('foo3'), triples)
        print(class_constraints.describe())
        self.assertEqual(len(errmsgs), 0)
        property_constraints = class_constraints.property_constraints_dict[TOOL.buildProject]
        self.assertEqual(property_constraints.onto_class_uri, rdflib.term.URIRef('foo3'))
        self.assertEqual(property_constraints.property_uri, TOOL.buildProject)
        self.assertEqual(property_constraints.min_cardinality, None)
        self.assertEqual(property_constraints.max_cardinality, None)
        self.assertEqual(property_constraints.value_range, None)
        self.assertEqual(property_constraints._qualified, None)


    def test_no_cardinality_with_range(self):
        '''
        TOOL.buildProject:  NO CARDINALITY STRING
        '''
        triples = [
            (rdflib.term.BNode('ub3bL88C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
             rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
            (rdflib.term.BNode('ub3bL88C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#buildProject')),
            (rdflib.term.BNode('ub3bL88C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction')),
        ]
        class_constraints, errmsgs = get_class_constraints(rdflib.term.URIRef('foo3a'), triples)
        print(class_constraints.describe())
        self.assertEqual(len(errmsgs), 0)
        property_constraints = class_constraints.property_constraints_dict[TOOL.buildProject]
        self.assertEqual(property_constraints.onto_class_uri, rdflib.term.URIRef('foo3a'))
        self.assertEqual(property_constraints.property_uri, TOOL.buildProject)
        self.assertEqual(property_constraints.min_cardinality, None)
        self.assertEqual(property_constraints.max_cardinality, None)
        self.assertEqual(property_constraints.value_range, XSD.string)
        self.assertEqual(property_constraints._qualified, None)


    def test_unqualified_with_range(self):
        '''
        TOOL.buildScript:  MIN STRING
        '''
        triples = [
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#buildScript')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
             rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#minCardinality'),
             rdflib.term.Literal('0', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger')))
        ]
        class_constraints, errmsgs = get_class_constraints(None, triples)
        print(class_constraints.describe())
        print(errmsgs)
        self.assertEqual(len(errmsgs), 1)
        property_constraints = class_constraints.property_constraints_dict[TOOL.buildScript]
        self.assertEqual(property_constraints.onto_class_uri, None)
        self.assertEqual(property_constraints.property_uri, TOOL.buildScript)
        self.assertEqual(property_constraints.min_cardinality, 0)
        self.assertEqual(property_constraints.max_cardinality, None)
        self.assertEqual(property_constraints.value_range, XSD.string)
        self.assertEqual(property_constraints._qualified, False)

    def test_unqualified_no_range(self):
        '''
        TOOL.compilationDate: UNQUALIFIED NO RANGE
        '''
        triples = [
            (rdflib.term.BNode('ub3bL53C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#compilationDate')),
            (rdflib.term.BNode('ub3bL53C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#maxCardinality'),
             rdflib.term.Literal('1', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
            (rdflib.term.BNode('ub3bL53C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction'))
        ]
        class_constraints, errmsgs = get_class_constraints(onto_class_uri = rdflib.term.URIRef('foo4'), triples = triples)
        print(class_constraints.describe())
        self.assertEqual(len(errmsgs), 0)
        property_constraints = class_constraints.property_constraints_dict[TOOL.compilationDate]
        self.assertEqual(property_constraints.onto_class_uri, rdflib.term.URIRef('foo4'))
        self.assertEqual(property_constraints.property_uri, TOOL.compilationDate)
        self.assertEqual(property_constraints.min_cardinality, None)
        self.assertEqual(property_constraints.max_cardinality, 1)
        self.assertEqual(property_constraints.value_range, None)
        self.assertEqual(property_constraints._qualified, False)


    def test_qualified_no_range(self):
        '''
        TOOL.compilationDate: QUALIFIED NO RANGE
        '''
        triples = [
            (rdflib.term.BNode('ub3bL53C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#compilationDate')),
            (rdflib.term.BNode('ub3bL53C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#maxQualifiedCardinality'),
             rdflib.term.Literal('1', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
            (rdflib.term.BNode('ub3bL53C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction'))
        ]
        class_constraints, errmsgs = get_class_constraints(onto_class_uri = None, triples = triples)
        print(class_constraints.describe())
        print(errmsgs)
        self.assertEqual(len(errmsgs), 1)
        property_constraints = class_constraints.property_constraints_dict[TOOL.compilationDate]
        self.assertEqual(property_constraints.onto_class_uri, None)
        self.assertEqual(property_constraints.property_uri, TOOL.compilationDate)
        self.assertEqual(property_constraints.min_cardinality, None)
        self.assertEqual(property_constraints.max_cardinality, 1)
        self.assertEqual(property_constraints.value_range, None)
        self.assertEqual(property_constraints._qualified, True)


    def test_qualified_with_range(self):
        '''
        TOOL.buildScript:  QUALIFIED MIN STRING
        '''
        triples = [
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#buildScript')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
             rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#minQualifiedCardinality'),
             rdflib.term.Literal('0', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
        ]
        class_constraints, errmsgs = get_class_constraints(rdflib.term.URIRef('foo2'), triples)
        print(class_constraints.describe())
        self.assertEqual(len(errmsgs), 0)
        property_constraints = class_constraints.property_constraints_dict[TOOL.buildScript]
        self.assertEqual(property_constraints.onto_class_uri, rdflib.term.URIRef('foo2'))
        self.assertEqual(property_constraints.property_uri, TOOL.buildScript)
        self.assertEqual(property_constraints.min_cardinality, 0)
        self.assertEqual(property_constraints.max_cardinality, None)
        self.assertEqual(property_constraints.value_range, XSD.string)
        self.assertEqual(property_constraints._qualified, True)



    def test_duplicate_conflicting(self):
        '''
        TOOL.buildScript:  Duplicate conflicting_cardinality
        '''
        triples = [
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#buildScript')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
             rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#minQualifiedCardinality'),
             rdflib.term.Literal('0', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#minQualifiedCardinality'),
             rdflib.term.Literal('1', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
        ]
        class_constraints, errmsgs = get_class_constraints(None, triples)
        print(class_constraints.describe())
        print(errmsgs)
        self.assertEqual(len(errmsgs), 1)
        property_constraints = class_constraints.property_constraints_dict[TOOL.buildScript]
        self.assertEqual(property_constraints.onto_class_uri, None)
        self.assertEqual(property_constraints.property_uri, TOOL.buildScript)
        self.assertEqual(property_constraints.min_cardinality, None)   # removed because conficting
        self.assertEqual(property_constraints.max_cardinality, None)
        self.assertEqual(property_constraints.value_range, XSD.string)
        self.assertEqual(property_constraints._qualified, None)   # because minCardinality removed conflicting

    def test_not_owl_restriction(self):
        '''
        TOOL.buildScript:  Not an owl.Restriction
        '''
        triples = [
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Something')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#buildScript')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
             rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#minQualifiedCardinality'),
             rdflib.term.Literal('0', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
        ]
        class_constraints, errmsgs = get_class_constraints(None, triples)
        print(errmsgs)
        print(class_constraints.describe())
        self.assertEqual(len(errmsgs), 1)


    def test_no_property(self):
        '''
        TOOL.buildScript:  Missing property uri
        '''
        triples = [
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
             rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#minQualifiedCardinality'),
             rdflib.term.Literal('1', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
        ]
        class_constraints, errmsgs = get_class_constraints(None, triples)
        print(errmsgs)
        print(class_constraints)
        print(class_constraints.describe())
        self.assertEqual(len(errmsgs), 1)


    def test_unsupported_predicate(self):
        '''
        TOOL.buildScript:  Unknown predicate
        '''
        triples = [
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#Restriction')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onProperty'),
             rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/tool#buildScript')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
             rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')),
            (rdflib.term.BNode('ub3bL94C3'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#unsupportedPredicate'),
             rdflib.term.Literal('1', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#nonNegativeInteger'))),
        ]
        class_constraints, errmsgs = get_class_constraints(None, triples)
        print(errmsgs)
        print(class_constraints)
        print(class_constraints.describe())
        self.assertEqual(len(errmsgs), 1)

if __name__ == '__main__':
    unittest.main()
