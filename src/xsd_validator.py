# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
This module implements a function that validates XSD data types.
'''
from io import StringIO, BytesIO
import re
from xml.sax.saxutils import escape
from lxml import etree
from rdflib.namespace import XSD    # Namespace('http://www.w3.org/2001/XMLSchema#')
from message import ErrorMessage


def validate_xsd(string, xsd_type):
    '''
    Arguments
        string     A string to be validated
        xsd_type   The string's required XSD type, a string or URIRef (see below)

    Return:
        List of ErrorMessage objects on error
        Empty list on success

    Error Conditions
        string is not a valid instance of xsd_type
        xsd_type is not a valid XSD type

    The xsd_type argument may be any of these:
        uri-style string, e.g. 'http://www.w3.org/2001/XMLSchema#integer'
        xml-style string, e.g. 'xsd:integer'
        uri-style URIRef, e.g. rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer')
        xml-style URIRef, e.g. rdflib.term.URIRef('xsd:integer')
    '''
    return XSDValidator().validate(string, xsd_type)


# ------------------ helper class --------------------------------

class Singleton(type):
    '''
    Metaclass for singleton class
    See https://stackoverflow.com/questions/6760685, Method 3
    '''
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class XSDValidator(metaclass=Singleton):
    '''
    This class uses the lxml library to cache XMLSchema objects
    for requested xsd types and apply them to strings
    '''
    # Class constants
    XSD_string = str(XSD)
    etree_errmsg_matcher = re.compile(r'(?:.*?): (.*)\., line \d+')
        # The first group is a non-captured non-greedy group of characters up to the first colon
        # The second group is the error message we want to capture
        # The rest describes position in local text, which we don't include in the error message


    def __init__(self):
        '''
        Create and return an empty instance of this class
        '''
        self.xml_schema = {}    # cache {xsd_type:XMLSchema}
        self.bad_xsd_type_errmsgs = {} # {xsd_type: ErrorMessage}


    def validate(self, string, xsd_type):
        '''
        Get XSLSchema for specified xsd_type, then use it to
        validate the specified string

        Arguments:
            string       The string string to be validated
            xml_schema   An XMLSchema object created by create_XMLSchema

        Return:
           List of zero or one ErrorMessage objects
        '''
        # Make sure this xsd_type is not blacklisted
        errmsgs = self.bad_xsd_type_errmsgs.get(xsd_type)
        if errmsgs:
            return errmsgs

        # Get the XMLSchema for this xsd_type
        # If this is a bad xsd_type, blacklist it
        try:
            xml_schema = self.get_xmlschema(xsd_type)
        except Exception as exc:
            errmsgs = [ErrorMessage(str(exc))]
            self.bad_xsd_type_errmsgs[xsd_type] = errmsgs
            return errmsgs

        # Use XMLSchema to validate the specified data string
        xml_snippet = '<value>{}</value>'.format(escape(string))
        try:
            xml_schema.assertValid(etree.parse(StringIO(xml_snippet)))
            return []
        except etree.DocumentInvalid as exc:
            return [ErrorMessage(message=self.parse_etree_errmsg(str(exc)))]
        except etree.XMLSyntaxError as exc:
            return [ErrorMessage(message=self.parse_etree_errmsg(str(exc)))]

    def get_xmlschema(self, xsd_type):
        '''
        If an XMLSchema object is for this xsd_type is cached, return it.
        Otherwise, create it, cache it, and return it.

        Arguments:
            xsd_type   An xsd type string

        Return:
            An etree.XMLSchema object

        Raise:
            Exception if xsd_type is not a valid xsd type
        '''
        # Convert xsd_type to string
        xsd_type_string = str(xsd_type)

        # If XMLSchema is cached for this string, return it
        xml_schema = self.xml_schema.get(xsd_type_string)
        if xml_schema:
            return xml_schema

        # Get XML-style and URI-style names for xsd_type
        # If xsd_type is not an XSD type, raise exception
        if xsd_type_string.startswith('xsd:'):
            xsd_type_xml = xsd_type_string
            xsd_type_uri = re.sub('xsd:', self.XSD_string, xsd_type_string)
        elif xsd_type_string.startswith(self.XSD_string):
            xsd_type_uri = xsd_type_string
            xsd_type_xml = re.sub(self.XSD_string, 'xsd:', xsd_type_string)
        else:
            raise Exception('Invalid xsd type {}'.format(xsd_type_string))

        # Create XMLSchema for this type, raise exception if invalid type
        xsd_schema_string = '''<?xml version="1.0" encoding="UTF-8" ?>
            <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                <xsd:element name="value"  type="{}"/>
            </xsd:schema>'''.format(xsd_type_xml)
        try:
            xml_schema =  etree.XMLSchema(file=BytesIO(xsd_schema_string.encode('ascii')))
        except etree.XMLSchemaParseError as exc:
            raise Exception(self.parse_etree_errmsg(str(exc)))

        # Cache XMLSchema under XML-style and URI-style names
        self.xml_schema[xsd_type_xml] = xml_schema
        self.xml_schema[xsd_type_uri] = xml_schema

        # Return the XMLSchema
        return xml_schema


    def parse_etree_errmsg(self, errmsg):
        '''
        Arguments:
            errmsg       An etree error message string

        Return:
            An error message without the etree cruft
        '''
        matcher = self.etree_errmsg_matcher.match(errmsg)
        if matcher:
            return matcher.group(1)
        else:
            return errmsg
