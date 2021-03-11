# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

import unittest
import rdflib
from rdflib.namespace import XSD
from datatype_constraints import get_datatype_constraints
VOCAB = rdflib.Namespace('https://unifiedcyberontology.org/ontology/uco/vocabulary#')


class TestDatatypeConstraints(unittest.TestCase):

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

    def test_vocabulary(self):
        '''
        <Class *https://unifiedcyberontology.org/ontology/uco/vocabulary:WindowsVolumeAttributeVocab*>
        '''
        triples = [
            (rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/vocabulary#WindowsVolumeAttributeVocab'),
             rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#comment'),
             rdflib.term.Literal('Defines an open-vocabulary of attributes that may be returned by the diskpart attributes command: http://technet.microsoft.com/en-us/library/cc766465(v=ws.10).aspx.', lang='en')),
            (rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/vocabulary#WindowsVolumeAttributeVocab'),
             rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'),
             rdflib.term.Literal('Windows Volume Attribute Vocabulary', lang='en-US')),
            (rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/vocabulary#WindowsVolumeAttributeVocab'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Datatype')),
            (rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/vocabulary#WindowsVolumeAttributeVocab'),
             rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'),
             rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Resource')),
            (rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/vocabulary#WindowsVolumeAttributeVocab'),
             rdflib.term.URIRef('http://www.w3.org/2002/07/owl#oneOf'),
             rdflib.term.BNode('f9ec04a0dce3d4832af9e9f13c4e606d5b727')),
            (rdflib.term.BNode('f9ec04a0dce3d4832af9e9f13c4e606d5b727'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#rest'),
             rdflib.term.BNode('f9ec04a0dce3d4832af9e9f13c4e606d5b728')),
            (rdflib.term.BNode('f9ec04a0dce3d4832af9e9f13c4e606d5b727'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#first'),
             rdflib.term.Literal('Hidden', datatype=rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/vocabulary#WindowsVolumeAttributeVocab'))),
            (rdflib.term.BNode('f9ec04a0dce3d4832af9e9f13c4e606d5b728'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#first'),
             rdflib.term.Literal('NoDefaultDriveLetter', datatype=rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/vocabulary#WindowsVolumeAttributeVocab'))),
            (rdflib.term.BNode('f9ec04a0dce3d4832af9e9f13c4e606d5b728'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#rest'),
             rdflib.term.BNode('f9ec04a0dce3d4832af9e9f13c4e606d5b729')),
            (rdflib.term.BNode('f9ec04a0dce3d4832af9e9f13c4e606d5b729'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#rest'),
             rdflib.term.BNode('f9ec04a0dce3d4832af9e9f13c4e606d5b730')),
            (rdflib.term.BNode('f9ec04a0dce3d4832af9e9f13c4e606d5b729'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#first'),
             rdflib.term.Literal('ReadOnly', datatype=rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/vocabulary#WindowsVolumeAttributeVocab'))),
            (rdflib.term.BNode('f9ec04a0dce3d4832af9e9f13c4e606d5b730'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#rest'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#nil')),
            (rdflib.term.BNode('f9ec04a0dce3d4832af9e9f13c4e606d5b730'),
             rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#first'),
             rdflib.term.Literal('ShadowCopy', datatype=rdflib.term.URIRef('https://unifiedcyberontology.org/ontology/uco/vocabulary#WindowsVolumeAttributeVocab')))]

        constraints, errmsgs = get_datatype_constraints(
           onto_class_uri = VOCAB.BuildConfigurationType,
           triples = triples)
        print(errmsgs)

        print(constraints)
        print(constraints.describe())
        print(vars(constraints))
        self.assertEqual(constraints.vocabulary, {'Hidden', 'NoDefaultDriveLetter', 'ReadOnly', 'ShadowCopy'})
        self.assertEqual(constraints.validate('ReadOnly'), [])
        print(constraints.validate('FOO'))
        self.assertEqual(len(constraints.validate('FOO')), 1)


if __name__ == '__main__':
    unittest.main()
