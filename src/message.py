# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
This module implements some trivial Message classes.
Their purpose is to provide a uniform way of formatting
error messages.
'''
import traceback
from namespace_manager import namespace_manager

class ErrorMessage:
    '''
    Base class for error message objects
    '''
    message_type = 'Error'
    def __init__(self,
            message=None,         # Message text
            message_source=None,  # Name of module, class or function producing this Error
            exc=None,             # Exception that was raised
            line_number=None,     # Line number (for errors in a line of data)
            onto_class_uri=None,  # Ontology class that this error pertains to
            property_uri=None):   # Property URI (string) that this error pertains to
        self.message = message
        self.onto_class_uri = onto_class_uri
        self.property_uri = property_uri
        self.line_number = line_number
        self.exc = exc
        self.caller = traceback.extract_stack(limit=2)[0].name
        # If you add another attribute, be sure to add it to __members()

    def describe(self):
        '''
        Build and return a string based on self's attribute values
        '''
        phrases = []
        if self.message_type:
            phrases.append('{}:'.format(self.message_type))
        if self.line_number:
            phrases.append('Line {},'.format(self.line_number))
#        if self.caller:   # REMOVED FOR DEMO
#            phrases.append('{}()'.format(self.caller))
        if self.onto_class_uri:
            phrases.append('Class {}'.format(pretty_uri(self.onto_class_uri)))
        if self.property_uri:
            phrases.append('Property {}'.format(pretty_uri(self.property_uri)))
        phrases.append('{}.'.format(self.message))
        if self.exc:
            phrases.append('{}: {}'.format(type(self.exc), self.exc))
        return ' '.join(phrases)

    def __str__(self):
        return self.describe()

    def __repr__(self):
        return self.describe()

    def __members(self):
        '''
        Two ErrorMessage objects are "equal" if they have the same
        value for all of these attributes.
        '''
        return (self.message_type, self.message, self.caller,
                self.exc, self.line_number, self.onto_class_uri, self.property_uri)

    def __eq__(self, other):
        '''
        Two ErrorMessage objects are "equal" if they have the same
        value for all of these attributes.
        '''
        if type(other) is type(self):
            return self.__members() == other.__members()
        else:
            return False

    def __hash__(self):
        '''
        Hash value consistent with "equality" condition.
        '''
        return hash(self.__members())



class DataError(ErrorMessage):
    message_type = 'Data Error'

class ConstraintError(ErrorMessage):
    message_type = 'Constraint Error'

class CriticalError(ErrorMessage):
    message_type = 'Critical Error'

class OntologyError(ErrorMessage):
    message_type = 'Ontology Error'

class UnsupportedFeature(ErrorMessage):
    message_type = 'Unsupported Feature'

class SoftwareBug(ErrorMessage):
    message_type = 'Software Bug'


def pretty_uri(uri):
    '''
    Arguments:
        uri   An rdflib.term.URIRef object

    Return:
        "pretty" string representation of uri
    '''
    try:
        return '<{}>'.format(uri.n3(namespace_manager))
    except Exception:
        return '<{}>'.format(uri)

def pretty_uris(uris):
    '''
    Arguments:
        uris   LIST of rdflib.term.URIRef objects

    Return:
        "pretty" string representation of list of uris
    '''
    return '[{}]'.format(', '.join([pretty_uri(uri) for uri in uris]))
