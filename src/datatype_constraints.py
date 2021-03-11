# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
This module manages ontology datatypes.
'''
import pprint
import rdflib
from rdflib.namespace import OWL, RDF, RDFS
from message import OntologyError, UnsupportedFeature, ConstraintError
from triples import get_spo_dict

class DatatypeError(Exception):
    '''
    Exception that carries a list of ErrorMessages.

    Usage:
        errmsgs = [ErrorMessage('foo'), ErrorMessage('bar')]
        try:
            raise DatatypeError(errmsgs)
        exception DatatypeError as exc:
            error_messages = exc.error_messages
    '''
    def __init__(self, *args):
        super().__init__(args)
        self.error_messages = args[0]


def get_datatype_constraints(onto_class_uri, triples):
    '''
    Build and return a DatatypeConstraints object for the specified list of triples

    Arguments:
        onto_class_uri  An rdflib.term.URIRef for the source ontology class
        triples         A list of triples from an ontospy.core.entities.OntoClass (e.g. onto_class.triples)

    Return:
        A tuple (DatatypeConstraints, LIST of ErrorMessage objects)
    '''
    # Convert list of triples to {subject:{predicate:{objects}}}
    spo_dict = get_spo_dict(triples)

    # Get parent_po_dict.  It's the only one whose key is not a BNode
    non_bnode_keys = [key for key in spo_dict.keys() if not isinstance(key, rdflib.term.BNode)]
    if not non_bnode_keys:
        errmsg = OntologyError(
            message = 'No parent node in triples: {}'.format(pprint.pformat(triples)),
            onto_class_uri=onto_class_uri)
        return None, [errmsg]
    elif len(non_bnode_keys) > 1:
        errmsg = OntologyError(
            message = 'Multiple parent nodes in triples: {}'.format(pprint.pformat(triples)),
            onto_class_uri=onto_class_uri)
        return None, [errmsg]
    else:
        parent_po_dict = spo_dict[non_bnode_keys[0]]

    # Proceed depending on database constraint type

    # Case 1: List of strings
    if parent_po_dict.get(RDFS.subClassOf) == {RDFS.Resource} and parent_po_dict.get(OWL.oneOf):
        try:
            datatype_constraints = VocabularyDatatypeConstraints(onto_class_uri, spo_dict)
            errmsgs = []
        except DatatypeError as exc:
            datatype_constraints = None
            errmsgs = exc.error_messages

    # Case 2: TBD

    # Otherwise
    else:
        datatype_constraints = None
        errmsg = UnsupportedFeature(
            message='Cannot figure out datatype for these triples:\n{}'.format(pprint.pformat(triples)),
            onto_class_uri=onto_class_uri)
        errmsgs = [errmsg]

    # Return results
    return datatype_constraints, errmsgs




class DatatypeConstraints:
    '''
    Base class of DatatypeConstraints classes.
    '''
    def __init__(self, onto_class_uri):
        '''
        Initialization common to all subclasses
        '''
        self.onto_class_uri = onto_class_uri

    def validate(self, value):
        '''
        Return:
            LIST of ErrorMessage object if value is not in self.vocabulary
            Empty List if value is OK

        Child class MUST override.
        '''
        raise NotImplementedError()

    def describe(self):
        '''
        Return:
            Description of self.

        Child class SHOULD override.
        '''
        return str(type(self))

    def __str__(self):
        return self.describe()



class VocabularyDatatypeConstraints(DatatypeConstraints):
    '''
    Class that validates strings that need to belong
    to a predefined set of strings (vocabulary)

    Attributes:
        vocabulary   Set of allowed strings
    '''
    def __init__(self, onto_class_uri, spo_dict):
        '''
        Create and initialize an instance of this class

        Arguments:
            onto_class_uri   The ontology class that is this Datatype
            spo_dict         Ontology {subject:{predicate:{value})}

        Raise:
            DatatypeError([ErrorMessage]): an Exception containing a LIST of ErrorMessages

        Algorithm:
            Naively assume the BNodes form a simple linked list, where the object
            of every RDF.first predicate is a Literal.  You don't have to follow the links
            in order, just catch all the RDF.firsts.
        '''
        super().__init__(onto_class_uri)
        errmsgs = []
        self.vocabulary = set()
        for subject, po_dict in spo_dict.items():
            if not isinstance(subject, rdflib.term.BNode):
                continue
            literals = po_dict.get(RDF.first)
            if len(literals) > 1:
                errmsgs.append(OntologyError(
                    message='Multiple values for RDF.first in linked list: {}'.format(literals),
                    onto_class_uri=onto_class_uri))
            elif literals:
                self.vocabulary.update([str(literal) for literal in literals])   # nondestructive

        if errmsgs:
            raise DatatypeError(errmsgs)


    def validate(self, value):
        '''
        Return:
            LIST of ErrorMessage object if value is not in self.vocabulary
            Empty List if value is OK
        '''
        if value in self.vocabulary:
            return []
        else:
            return [ConstraintError(
                message='value "{}" not in vocabulary {}'.format(value, self.vocabulary),
                onto_class_uri=self.onto_class_uri)]

    def describe(self):
        '''
        Describe self in plain text
        '''
        return 'VocabularyDatatypeConstraint: one of {}'.format(self.vocabulary)
