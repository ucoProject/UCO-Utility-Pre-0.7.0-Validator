# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.
'''
This module implements the Context class.

Definitions:
    URI.                         A Universal Resource Indicator.
    URI string.                  A URI represented as a string, e.g. 'http://www.w3.org/2001/XMLSchema#integer'.

    Namespace.                   A location of a group of related URIs.
    Namespace string.            A namespace represented as a string, e.g.'http://www.w3.org/2001/XMLSchema#'.

    Name.                        A property, class or object identifier.
    Name string.                 A name represented as a string, e.g. 'integer'.

    Qualifier.                   An abbreviation for a namespace string, e.g. 'xsd' abbreviates 'http://www.w3.org/2001/XMLSchema#'.
    Binding.                     Association of a qualifier with a namespace.
    Namespace mapping.           A mapping that relates Qualifiers to namespace strings.
    Inverse namespace mapping.   A mapping from namespace strings to qualifiers.
    Qualified name or Qname.     A uri represented as a qualifier and name string relative to a namespace mapping.

    Context.                     A set of namespace mappings.
    Context object.              An instance of the class implemented in this module.

    Normalized URI Object.       An instance of rdflib.term.URIRef that describes a URI string.
    Normalized Namespace Obj.    An instance of rdflib.Namespace that describes a namespace string.
'''
import rdflib

class Context:
    '''
    This class encapsulates a set of namespaces and provides
    functions to manipulate qnames and uris within them.

    Attributes:
        self.namespace_mapping =  {}         # {qualifier_string:namespace_string}
        self.inverse_namespace_mapping = {}  # {namespace_string:qualifier_string}
        self.bindings = [()]                 # list of [(qualifier, namespace)] in the order they were applied
        self.default_qualifiers = set()      # [qualifier_string] (CONSTANT)
        self.default_namespaces = set()      # [namespace_string] (CONSTANT)

    Methods:
        bind(qualifier, namespace)        Assign qualifier to namespace
        populate([(qualifier, namespace]) Assign qualifiers to namespaces
        namespace(qualifier)              Convert qualifier to namespace string if possible
        qualifier(namespace)              Convert namespace string to qualifier if possible
        split_qname(identifier)           Derive (qualifier string, name string) from identifier if identifier is a qname
        split_uri(identifier)             Derive (namespace string, name string) from identifier if identifier is a uri
        qname(identifier)                 Express identifier as qname string if possible
        uri_string(identifier)            Express identifier as uri string if possible
        uri_object(identifier)            Express identifier as normalized rdflib.term.URIRef instance if possible
        format(identifier_or_list)        Format identifier or list of identifiers as a pretty string, using qnames where possible
    '''
    # Class constants
    DEFAULT_BINDINGS = [
         ('rdf','http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
         ('rdfs','http://www.w3.org/2000/01/rdf-schema#'),
         ('xsd','http://www.w3.org/2001/XMLSchema#'),
         ('owl','http://www.w3.org/2002/07/owl#'),
         ('sh','http://www.w3.org/ns/shacl#'),
         ('olo','http://purl.org/ontology/olo/core#'),
    ]
    DEFAULT_QUALIFIERS = {t[0] for t in DEFAULT_BINDINGS}
    DEFAULT_NAMESPACES = {t[1] for t in DEFAULT_BINDINGS}

    # Creator
    def __init__(self):
        '''
        Create an empty instance of this class
        '''
        self.namespace_mapping =  {}         # {qualifier_string:namespace_string}
        self.inverse_namespace_mapping = {}  # {namespace_string:qualifier_string}
        self.bindings = []                   # [(qualifier_string, namespace_string)] in order applied
        self.populate(Context.DEFAULT_BINDINGS)

    # Add binding
    def bind(self, qualifier, namespace):
        '''
        Arguments:
            qualifier   An object whose str() produces a qualifier, e.g. 'xsd'
            namespace   An object whose str() produces a namespace string, e.g. 'http://www.w3.org/2001/XMLSchema#'
                 In particular, this could be a string, rdflib.Namespace or a rdflib.term.URIRef.

        Return:
            self, with addtional binding

        Action:
            Add binding to this Context

        Note: Last one wins!
            If qualifier_string is already in self.namespace_mapping, the new one replaces it.
            If namespace_string is already in self.inverse_namespace_mapping, the new one replaces it.
        '''
        qualifier_string = str(qualifier)
        namespace_string = str(namespace)
        self.bindings.append((qualifier, namespace))

        # If qualifier is already in the forward mapping, clobber existing value
        self.namespace_mapping[qualifier_string] = namespace_string

        # Computing the inverse mapping is tricky because of ontospy's namespaces
        # Rule 1:  If there is no existing reverse mapped qualifier, bind the new qualifier
        # Rule 2:  If the existing mapped qualifier is the empty string, bind new qualifier
        existing_inverse_value = self.inverse_namespace_mapping.get(namespace_string)
        if not existing_inverse_value:
            self.inverse_namespace_mapping[namespace_string] = qualifier_string

        # Rule 3:  If there is any existing mapped qualifier and the new one is the empty string, do not bind it
        elif not qualifier_string:
            pass

        # Rule 4:  If the existing mapped qualifier ends with a digit, bind the new one
        elif existing_inverse_value[-1] in '0123456789':
            self.inverse_namespace_mapping[namespace_string] = qualifier_string

        # Rule 5:  If the existing mapped qualifier does not end with a digit and the new one does, do not bind
        elif qualifier_string[-1] in '0123456789':
            pass
        # Rule 6:  If none of the above, clobber existing mapped qualifier with new one (last one wins)
        else:
            self.inverse_namespace_mapping[namespace_string] = qualifier_string

        return self


    # Add bindings
    def populate(self, bindings):
        '''
        Arguments:
            bindings    LIST of (qualifier, namespace), e.g. ontospy.namespaces

        Return:
            self, populated

        Action:
            Add bindings to the Context.

        Note: Last one wins!
            If qualifier is already in self.namespace_mapping, the new one replaces it.
            If namespace is already in self.inverse_namespace_mapping, the new one replaces it.
        '''
        for qualifier, namespace in bindings:
            self.bind(qualifier, namespace)
        return self


    # qualifier -> namespace
    def namespace(self, qualifier):
        '''
        Arguments:
            qualifier   An object whose str() may be a qualifier string

        Return:
            The corresponding namespace string if qualifier is in this Context
            None if not
        '''
        return self.namespace_mapping.get(str(qualifier))


    # namespace -> qualifier
    def qualifier(self, namespace):
        '''
        Arguments:
            namespace   An object whose str() may be namespace string

        Return:
            The corresponding qualifier string if namespace is in this Context
            None if not
        '''
        return self.inverse_namespace_mapping.get(str(namespace))


    # identifier -> (qualifier, name)
    def split_qname(self, identifier):
        '''
        Arguments
            identifier    An object whose str() which may be a qname

        Return:
            (qualifier_string, name_string)  if string is a qname with a qualifier in this Context
            (str(identifier), None)          otherwise
        '''
        string = str(identifier)
        result = string.split(':', 1)   # (stuff before first colon, stuff after first colon)

        # If no colon in string, it's certainly not a qname
        if len(result) == 1:
            return (string, None)

        # If colon in string and first part in mapping, it's a qname
        qualifier_string, name = result
        if qualifier_string in self.namespace_mapping:
            return (qualifier_string, name)

        # If colon in string but first part not in mapping, it's not a qname
        return (string, None)


    # identifier -> (namespace, name)
    def split_uri(self, identifier):
        '''
        Arguments
            identifier    An object whose str() may be a uri

        Return:
            (namespace_string, name_string)  if string is a uri with a namespace string in this Context
            (str(identifier), None)          otherwise
        '''
        string = str(identifier)

        # If string starts with a known namespace, return namespace and name
        for namespace_string in self.inverse_namespace_mapping:
            if string.startswith(namespace_string):
                return (namespace_string, string[len(namespace_string):])

        # If not, it's not a uri
        return (string, None)


    # identifier -> qname
    def qname(self, identifier):
        '''
        Arguments
            identifier    An object whose str() may be a qname, a uri, or something else

        Return:
            qname_string  If identifier is a qname or a uri that can be coverted to a qname in this Context
            None          If none of the above.
        '''
        string = str(identifier)

        # If it's a qname, return the qname string
        _qualifier, name = self.split_qname(string)
        if name is not None:
            return string

        # If it's a uri, convert to qname and return the qname string
        namespace, name = self.split_uri(string)
        if name is not None:
            return '{}:{}'.format(self.inverse_namespace_mapping[namespace], name)

        # If none of the above, return None
        return None



    # identifier -> uri_string
    def uri_string(self, identifier):
        '''
        Arguments
            identifier    An object whose str() may be a qname, a uri, or something else

        Return:
            uri_string    If identifier is a uri or a qname that can be coverted to a uri in this Context
            None          If none of the above.
        '''
        string = str(identifier)

        # If it's a qname, convert to uri and return the uri string
        qualifier, name = self.split_qname(string)
        if name is not None:
            return '{}{}'.format(self.namespace_mapping[qualifier], name)

        # If it's a uri, return the uri string
        _namespace, name = self.split_uri(string)
        if name is not None:
            return string

        # If it's none of the above, return None
        return None


    # identifier -> rdflib.term.URIRef(uri_string)
    def uri_object(self, identifier):
        '''
        Arguments:
            identifier    An object whose str() may be a qname, a uri, or something else

        Return:
            Normalized reflib.term.URIRef    If identifier is a uri or a qname that can be coverted to a uri in this Context
            None                             If none of the above
        '''
        # If identifier is a uri or a qname in this namespace, return uri string
        uri = self.uri_string(identifier)
        if uri:
            return rdflib.term.URIRef(uri)

        # If not, return None
        return None


    # identifier(s) -> formatted string
    def format(self, identifier_or_list):
        '''
        Arguments:
            identifier_or_list
                Either an object whose str() may be a qname, a uri, or something else,
                OR
                A LIST of objects whose str() may be a qname, a uri, or something else

        Return:
            A "pretty" string representation of the identifier or list of identifiers,
            using qnames where possible.
        '''
        # Subfunction to prettify a single identifier
        def _prettify(identifier):
            string = str(identifier)

            # Return qname string if possible
            qname = self.qname(string)
            if qname is not None:
                return '<{}>'.format(qname)

            # Return identifier string if not
            return '<{}>'.format(string)

        # Main function to prettify the input argument
        if isinstance(identifier_or_list, (list, tuple, set)):
            return '[{}]'.format(', '.join([_prettify(identifier) for identifier in identifier_or_list]))
        else:
            return _prettify(identifier_or_list)  # identifier_or_list is just an identifier
