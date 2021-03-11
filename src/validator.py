# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
This module is where the ontology and casedata meet.
'''
import json
import rdflib
from rdflib.namespace import RDF, XSD
from triples import get_spo_dict
from class_constraints import ClassConstraints
from message import DataError, UnsupportedFeature, ConstraintError 
from message import pretty_uri, pretty_uris
from namespace_manager import namespace_manager
from datatype_constraints import DatatypeConstraints
from xsd_validator import validate_xsd
namespaces = dict(namespace_manager.namespaces())  # {'prefix':URIRef('http:/blah/blah#')}



def validate(ontology, case_data):
    '''
    Arguments:
        ontology   An Ontology object
        case_data  A CaseData object

    Return:
        List of ErrorMessage objects sorted by line number
    '''
    # Convert case_data triples to SPO dictionary {subject:{predicate:{objects}}}
    spo_dict = get_spo_dict(case_data.graph[::])

    # Call validate_case_data
    error_messages = validate_case_data(spo_dict, case_data.line_numbers,
        ontology.constraints, ontology.property_ranges)

    # Return error messages sorted by line number
    error_messages.sort(key=lambda x: x.line_number if x.line_number else 0)
    return error_messages


def validate_case_data(spo_dict, line_numbers, ontology_constraints, ontology_property_ranges):
    '''
    Arguments:
        spo_dict                  case_data triples in dictionary {subject:{predicate:{objects}}}
        line_numbers              case_data {subject_uri:line_number}
        ontology_constraints      ontology {onto_class_uri:ClassConstraints|DatatypeConstraints|None}
        ontology_property_ranges  ontology {property_uri:range_uri|None}

    Return:
        List of error messages

    Note: We avoid passing the full ontology and case_data objects to facilitate unit testing
    '''
    # Start with an empty list of error messages
    error_messages = []

    # Do for each case_data triples Subject
    for subject, po_dict in spo_dict.items():
        line_number = line_numbers.get(subject)

        #print()
        #print('subject', subject)

        # Get Subject's type, which should be a Class in the ontology
        # Make sure there's exactly one type. If it isn't, skip this Subject
        subject_type_uris = po_dict.get(RDF.type)

        # If subject has no type, error
        if not subject_type_uris:
            #print('Skipping subject {} because it has no type'.format(subject))
            error_messages.append(DataError(
                message='{} has no ranges'.format(subject),
                line_number=line_number))
            continue

        # If subject has more than one type, error
        if len(subject_type_uris) > 1:
            #print('Skipping subject {} because it has {} types {}'.format(subject, len(subject_type_uris), subject_type_uris))
            error_messages.append(DataError(
                message='{} has {} types: {}'.format(
                    pretty_uri(subject),
                    len(subject_type_uris),
                    pretty_uris(subject_type_uris)),
                line_number=line_number))
            continue

        subject_type_uri = list(subject_type_uris)[0]
        #print('{} is a {}'.format(subject, subject_type_uri))


        # Make sure Subject's type exists in the ontology.  If it doesn't, skip this Subject
        # ontology.constraints maps all ontology classes to constraint objects (or None)
        if not subject_type_uri in ontology_constraints:
            #print('Skipping subject {} because type {} not in ontology'.format(subject, subject_type_uri))
            error_messages.append(DataError(
                message='class not in ontology',
                onto_class_uri = subject_type_uri,
                line_number=line_number))
            continue
        #print('{} found in ontospy'.format(subject_type_uri))


        # This Subject's predicates and objects are in po_dict.
        # Except for RDF.type, predicates are properties and the objects are their values.
        # Find the type of each value and build pvt_dict={predicate:{value:type}}.
        # See get_value_type() for details on how this is done
        pvt_dict = {}    # {property:{value:type}}
        for predicate, objects in po_dict.items():
            if predicate == RDF.type:   # Skip non-property predicates
                continue
            pvt_dict[predicate] = {}
            for value in objects:
                value_type, errmsgs = get_value_type(value, spo_dict)
                for errmsg in errmsgs:
                    errmsg.onto_class_uri = subject_type_uri
                    errmsg.line_number = line_number
                error_messages.extend(errmsgs)
                pvt_dict[predicate][value] = value_type
        #print('{} has pvt_dict of length {}'.format(subject, len(pvt_dict)))


        # Get the constraints object for Subject type's ontology class.
        # It should be an instance of ClassConstraints or None.
        # If it's something else, use None, and flag an error.
        class_constraints = ontology_constraints.get(subject_type_uri)
        if class_constraints and not isinstance(class_constraints, ClassConstraints):
            error_messages.append(UnsupportedFeature(
                message='expected ClassConstraints, found {}'.format(type(class_constraints)),
                onto_class_uri = subject_type_uri,
                line_number=line_number))
        #print('{} is subject to {}'.format(subject, class_constraints))

        # If constraints is ClassConstraints, validate cardinality constraints
        if isinstance(class_constraints, ClassConstraints):
            errmsgs = validate_cardinality_constraints(pvt_dict, class_constraints)
            for errmsg in errmsgs:
                errmsg.onto_class_uri = subject_type_uri
                errmsg.line_number = line_number
        error_messages.extend(errmsgs)
        #print('Validating cardinality constraints for {} got {} error messages'.format(subject, len(errmsgs)))

        # Validate property range constraints, with or without ClassConstraints
        if isinstance(class_constraints, ClassConstraints):
            errmsgs = validate_range_constraints(pvt_dict, ontology_property_ranges, class_constraints)
        else:
            errmsgs = validate_range_constraints(pvt_dict, ontology_property_ranges)
        for errmsg in errmsgs:
            errmsg.onto_class_uri = subject_type_uri
            errmsg.line_number = line_number
        #print('Validating property range constraints for {} got {} error messages'.format(subject, len(errmsgs)))

        # Validate the literals
        for property_uri, vt_dict in pvt_dict.items():
            errmsgs = validate_literals(
                literals=[value for value in vt_dict.keys() if isinstance(value, rdflib.term.Literal)],
                ontology_constraints=ontology_constraints)
            for errmsg in errmsgs:
                errmsg.line_number = line_number
                errmsg.property_uri = property_uri
                errmsg.onto_class_uri = subject_type_uri
        #print('Validating literals for {} got {} error messages'.format(subject, len(errmsgs)))

    # Done!  Return error messages
    return error_messages



def validate_cardinality_constraints(pvt_dict, class_constraints):
    '''
    Arguments:
        pvt_dict                  data {property_uri:{value:type_uri}}
        class_constraints         A ClassConstraints object

    Return:
        List of ErrorMessage objects
    '''
    # Start with an empty list of error messages
    error_messages = []

    # Make sure REQUIRED properties are present
    required_properties = class_constraints.get_required_properties()
    for required_property in required_properties:
        if required_property.n3(namespace_manager) == 'core:id':   # This property is exempt
            continue
        if required_property not in pvt_dict:
            error_messages.append(ConstraintError(
                message='data is missing required property',
                property_uri=required_property))

    # Make sure properties with cardinality constraints meet the constraints
    for property_uri, vt_dict in pvt_dict.items():
        property_constraints = class_constraints.get_property_constraints(property_uri)
        if property_constraints and property_constraints.min_cardinality is not None:
            if len(vt_dict) < property_constraints.min_cardinality:
                error_messages.append(ConstraintError(
                    message='property has {} values but must have at least {}'.format(
                        len(vt_dict), property_constraints.min_cardinality),
                    property_uri=property_uri))
        if property_constraints and property_constraints.max_cardinality is not None:
            if len(vt_dict) > property_constraints.max_cardinality:
                error_messages.append(ConstraintError(
                    message='property has {} values but must have at most {}'.format(
                        len(vt_dict), property_constraints.max_cardinality),
                    property_uri=property_uri))

    # Done
    return error_messages



def validate_range_constraints(pvt_dict, ontology_property_ranges, class_constraints=None):
    '''
    Arguments:
        pvt_dict                  data {property_uri:{value:type_uri}}
        ontology_property_ranges  ontology.property_ranges, {property_uri:range_uri|None}
        class_constraints         A ClassConstraints object or None

    Return:
        List of ErrorMessage objects
    '''
    # Start with an empty list of error messages
    error_messages = []

    # Check property ranges for each property
    for property_uri, vt_dict in pvt_dict.items():

        # Identify property's range
        # If there's a class_constraint and it has a range, use that range.
        # Otherwise if there's a "global" property range, use that range.
        # Otherwise, there's no range, do there's nothing to check
        property_range = None
        if class_constraints:
            property_constraints = class_constraints.get_property_constraints(property_uri)
            if property_constraints:
                property_range = property_constraints.value_range   # could be None

        if not property_range:
            property_range = ontology_property_ranges.get(property_uri)   # could still be None


        # If there's a property range, check that each value's type is in the property range
        #  TODO: Allow value_type to be an instance of a *subclass* of property_range
        if property_range:
            for value, value_type in vt_dict.items():
                if value_type != property_range:   # TODO: if not a subclass of property_range
                    error_messages.append(ConstraintError(
                        message="property's value {} is a {} but must be a {}".format(
                            value, value_type, property_range),
                        property_uri=property_uri))

    # Done!  Return error_messages
    return error_messages




def validate_literals(literals, ontology_constraints):
    '''
    Arguments:
        literals                List of rdflib.term.Literal values
        ontology_constraints  ontology.constraints,
                                {onto_class_uri:ClassConstraints|DatatypeConstraints|None}

    Return:
        List of ErrorMessage objects

    Blacklisted types:
        If literal has no datatype, it is by default a string, so no need to validate.
        If literal datatype is XSD.base64Binary, ontospy already converted its value to binary,
            so we cannot validate it.  If the base64 were invalid, ontospy would have reported it.
    '''
    # Start with empty list of error messages
    error_messages = []

    # Do for each value
    for literal in literals:

        # If Literal has no datatype, it is an XSD.string by default.  No check needed.
        if literal.datatype is None:
            continue

        # If Literal is a blacklisted type, do not check
        if literal.datatype == XSD.base64Binary:
            continue

        # If Literal is not a URIRef, UnsupportedFeature
        if not isinstance(literal.datatype, rdflib.term.URIRef):
            error_messages.append(UnsupportedFeature(
                message='Literal has datatype that is not a URIRef: {}'.format(literal)))
            continue

        # If Literal datatype is an XSD type, do validate XSD
        # TODO: Is this really necessary?
        if str(literal.datatype).startswith(XSD):
            error_messages.extend(validate_xsd(str(literal), literal.datatype))
            continue

        # If we're here, Literal datatype is a URIRef and not an XSD type.
        # If it's not a Datatype, error.
        datatype_constraints = ontology_constraints.get(literal.datatype)
        if not isinstance(datatype_constraints, DatatypeConstraints):
            error_messages.append(UnsupportedFeature(
                message='Literal has unrecognized datatype: {}'.format(literal)))
            continue

        # Call datatypeConstraint's validate function and return results
        error_messages.extend(datatype_constraints.validate(str(literal)))

    # Done! Return error messages
    return error_messages



def get_value_type(value, spo_dict):
    '''
    Arguments:
        value        A value (object of a predicate) from the CaseData
        spo_dict     The CaseData triples {subject:{predicate:{objects}}}

    Return:  tuple containing
        The value's data type as a rdflib.term.URIRef, possibly None
        A LIST of ErrorMessage objects

    Cases:
        1. If value is a Literal, its type is the literal's datatype
        2. If value is a BNode, its type is the BNode's RDF.type
        3. If value is a URIRef, its points to an local object and its type is the local object's RDF.type
        In all cases, if a value or its type cannot be found or is invalid, this function returns None

    Geek note:
        spo_dict is a defaultdict.
        If you try to get spo_dict[value] and value is not in the dict, it changes the dict's size
        This causes an error when iterating over the dict.
        Therefore, we must use spo_dict.get(value) instead of spo_dict[value]
    '''
    # Case 1.  Value is a Literal (spo_dict not used in this case)
    if isinstance(value, rdflib.term.Literal):
        literal = value

        # If literal.datatype is None, return XSD.string and no errors
        if literal.datatype is None:
            return XSD.string, []

        # If literal.datatype is "good", return it with no errors
        datatype_string = str(literal.datatype)
        if datatype_string.startswith('http://') or datatype_string.startswith('https://'):
            return literal.datatype, []

        # If it's is of the form something:something, try to expand it
        tokens = datatype_string.split(':',1)
        if len(tokens) == 2:
            prefix, rest = tokens

            # If prefix is known, return URI with expanded prefix and no errors
            expanded_prefix = namespaces.get(prefix)
            if expanded_prefix:
                return rdflib.term.URIRef(expanded_prefix + rest), []

            # If prefix is unknown, return None and error
            errmsg = DataError(message='unknown prefix in literal datatype {}'.format(literal.datatype))
            return None, [errmsg]

        # If it isn't even of the form something:something, return None and error
        errmsg = DataError(message='unsupported datatype {}'.format(literal.datatype))
        return None, [errmsg]


    # Case 2 and 3.  Value is a BNode or URIRef
    elif isinstance(value, (rdflib.term.BNode, rdflib.term.URIRef)):
        link = value
        link_description = value.__class__.__name__.split('.')[-1]

        # Get the BNode or URIRef link
        po_dict = spo_dict.get(link)

        # If the link is broken, return None with error message
        if not po_dict:
            errmsg = DataError(message='malformed case data: missing link <{}>'.format(link))
            return None, [errmsg]

        # Get the BNode or URIRef's types
        datatypes = po_dict.get(RDF.type)   # SET of classes (URIRefs), should have only one member

        # If there are zero or multiple types, data is malformed
        if not datatypes:
            errmsg = DataError(message='malformed case data: {} {} has no datatypes'.format(link_description, pretty_uri(link)))
            return None, [errmsg]
        if len(datatypes) > 1:
            errmsg = DataError(message='malformed case data: {} <{}> has {} datatypes {}'.format(
                link_description,
                pretty_uri(link),
                len(datatypes),
                pretty_uris(datatypes)))
            return None, [errmsg]

        # If we're here, datatype has one value.  Return it with no error
        return list(datatypes)[0], []

    # Case 4.  Unexpected Value type
    errmsg = DataError(
        message='unrecognized data value {} of type {}, expected a Literal, URIRef or BNode'.format(
            value, type(value)))
    return None, [errmsg]




# Json encoder to support sets
class SetEncoder(json.JSONEncoder):
    '''
    A Json Encoder class that treats sets as lists.

    Usage:  json.dumps(spo_dict, indent=2, cls=SetEncoder)
    '''
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)
