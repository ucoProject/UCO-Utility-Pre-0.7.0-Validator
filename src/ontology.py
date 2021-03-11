# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
This module implements the Ontology object.

An instance of this object contains the classes and properties
derivied from applying Ontospy to the input files.
'''
from copy import deepcopy
import datetime
import os
from ontospy import Ontospy
from rdflib.namespace import OWL, RDFS
import serializer
from class_constraints import get_class_constraints, ClassConstraints
from datatype_constraints import get_datatype_constraints
import namespace_manager
from message import OntologyError, UnsupportedFeature
from message import pretty_uri, pretty_uris

VERSION = '1.0'   # Appears in the metadata when serialized

def get_ontology(path, verbose=True, **kwargs):
    '''
    If path is a serialized ongology file, deserialize it and return it.
    If path is a directory that contains turtle files, build Ontology object from scratch.
    If path is something else, raise exception.

    Arguments:
        path     Full path to a serialized ontology file or a directory containing turtle files
        verbose  If true and using Ontospy, Ontospy library runs verbosely
        kwargs   Additional arguments passed on to Ontospy

    Return:
        An Ontology object

    Side effect:
        This function populates namespace_manager.namespace_manager

    Raise:
        Exception if path is not a serialized ontology file or a directory containing turtle files
    '''
    # Start with empty Ontology object
    ontology = Ontology()

    # If path is a serialized ontology file, deserialize it and populate namespace_manager
    if os.path.isfile(path) and serializer.get_identifier(path) == serializer.ONTOLOGY:
        _identifer, _metadata, ontology.__dict__ = serializer.deserialize(path)
        namespace_manager.populate(ontology.constraints.keys())

    # If path is a directory containing turtle files, build Ontology object AND populate namespace_manager
    # Note: _read_turtle_files() populates the namespace_manager so the ontology errors can use it
    elif os.path.isdir(path) and [filename for filename in os.listdir(path) if filename.endswith('.ttl')]:
        ontology.__dict__ = _read_turtle_files(path, verbose, **kwargs)

    # If path is something else, raise
    else:
        raise Exception('{} is neither a serialized ontology file nor a directory containing turtle files'.format(path))

    # Populate the namespace from the ontology classes

    # Return the ontology object
    return ontology



class Ontology:
    '''
    This class contains ontology information derived from having ontospy ingest turtle files.

    Attributes:
        turtle_dirpath    The path to the directory containing the turtle files
        constraints       {URIRef(onto_class):ClassConstraints|DatatypeConstraints|None} (derived from ontospy.all_classes
        property_ranges   {property_uri:range_uri|None}  (derived from ontospy.all_properties)
        error_messages    {ErrorMessage}   Set of instances of ErrorMessage or subclass objects
    '''
    def __init__(self):
        self.turtle_dirpath = None   # The path to the directory containing the turtle files
        self.constraints = {}        # {URIRef(onto_class):ClassConstraints|DatatypeConstraints|None}
        self.property_ranges = {}    # {property_uri:range_uri|None}
        self.error_messages = {}     # {ErrorMessage}

    def serialize(self, output_filepath, comment):
        '''
        Serialize this object and write it to the specified output file.

        Argument:
            output_filepath    Full path of file to receive the serialized object
            comment            A comment string to include in the serialized object
        '''
        identifier = serializer.ONTOLOGY
        dir_hash, dir_manifest = serializer.get_hash_and_manifest(self.turtle_dirpath)
        metadata = {
            'comment': comment,
            'version': VERSION,
            'path': os.path.abspath(self.turtle_dirpath),
            'timestamp': datetime.datetime.now().isoformat(),
            'md5': dir_hash,
            'manifest': dir_manifest
        }
        serializer.serialize(identifier, metadata, self.__dict__, output_filepath)



def _read_turtle_files(turtle_dirpath, verbose=True, **kwargs):
    '''
    Load and parse the turtle files in the turtle_dirpath.

    Arguments:
        turtle_dirpath    Full path to the directory containing turtle files
        verbose           If true, Ontospy library runs verbosely
        kwargs            Additional arguments passed on to Ontospy

    Return:  dictionary
        {
            'turtle_dirpath':dirpath, # Path to the directory containing the turtle files
            'property_ranges':value,  # {property_uri:range_uri|None}  (derived from ontospy.all_properties)
            'constraints':value,      # {URIRef(onto_class):constraints} (derived from ontospy.all_classes)
            'error_messages':[errmsg] # List of unique ErrorMessage objects
        }
        where constraints is an instance of ClassConstraints, DatatypeConstraints or None
    '''
    # Step 0.  Initialize
    error_messages = set()

    # Step 1.  Build Ontospy
    ontospy = Ontospy(uri_or_path=turtle_dirpath, rdf_format='turtle', verbose=verbose, **kwargs)

    # Step 1A.  Populate namespace_manager
    namespace_manager.populate([onto_class.uri for onto_class in ontospy.all_classes])

    # Step 2.  Get naive constraints for each class
    simple_constraints_dict = {}    # {URIRef(class):ClassConstraints|DatatypeConstraints|None}
    for onto_class in ontospy.all_classes:
        if onto_class.rdftype == OWL.Class:
            simple_constraints, errmsgs = get_class_constraints(onto_class.uri, onto_class.triples)
        elif onto_class.rdftype == RDFS.Datatype:
            simple_constraints, errmsgs = get_datatype_constraints(onto_class.uri, onto_class.triples)
        else:
            simple_constraints = None

        simple_constraints_dict[onto_class.uri] = simple_constraints

    # Step 3.  Merge ancestor naive constraints into constraints for each class.
    parent_child_class_dict = {}
    for parent_onto_class, child_onto_classes in ontospy.ontologyClassTree().items():
        if parent_onto_class != 0:
            parent_child_class_dict[parent_onto_class.uri] = [child_onto_class.uri for child_onto_class in child_onto_classes]
    net_constraints, errmsgs = _inherit_constraints(simple_constraints_dict, parent_child_class_dict)
    error_messages.update(errmsgs)

    # Step 4.  Get property ranges from ontospy.all_properties
    ontospy_property_ranges = {}    # Intermediate value: {property_uri: [range_uri]}
    ontospy_property_triples = {}   # Intermediate value: {property_uri: [triples]}
    for onto_property in ontospy.all_properties:   # OntoProperty objects
        ontospy_property_ranges[onto_property.uri] = [property_range.uri for property_range in onto_property.ranges]
        ontospy_property_triples[onto_property.uri] = onto_property.triples

    property_ranges, errmsgs = _get_property_ranges(ontospy_property_ranges, ontospy_property_triples)
    error_messages.update(errmsgs)

    # Step 5.  Check that range constraints are consistent with general property constraints
    errmsgs = _check_range_consistency(simple_constraints_dict, property_ranges)
    error_messages.update(errmsgs)


    # Construct and return dictionary
    return {
        'turtle_dirpath': turtle_dirpath,
        'property_ranges': property_ranges,
        'constraints': net_constraints,
        'error_messages': sorted(list(error_messages), key=lambda x:(x.onto_class_uri, x.property_uri))
    }



def _inherit_constraints(constraints, parent_child_class_dict):
    '''
    This function belongs in the Ontology class.
    It is implemented outside the Ontology class to facilitate unit testing

    Arguments:
        constraints               Dictionary {onto_class_uri:ClassConstraints|DatatypeConstraints|None}
        parent_child_class_dict   Dictionary {parent_onto_class_uri:[child_onto_class_uri]}

    Return:  tuple of
        net_constraints   New constraints dictionary with merged ClassConstraints (other contents not changed)
        error_messages    List of ErrorMessage objects

    Copy constraints into net_constraints, then use the algorithm below to
    compute for each class that has ClassConstraints the result of "inheriting"
    from the ClassConstraints all its ancestor classes.

    Algorithm:
        Do until not changed:
            changed = False
            For each parent-child ontology class pair
                Make sure both parent and child class have a ClassConstraint
                If both parent and child class have property constraint for property P
                    replace child's constraint by net constraint
                    changed = True if the replacement is different from the original
                Else if parent class has property constraint for property P and child class does not,
                    copy property constraint for P to child
                    changed = True
    '''
    # For debugging
    #def print_net_constraints():
    #    print(100*'*')
    #    print('net_constraints')
    #    for key, value in net_constraints.items():
    #        print('{}:'.format(key))
    #        print('{}'.format(value))
    #    print()

    # Initialize
    net_constraints = deepcopy(constraints)     # {onto_class_uri:ClassConstraints|other}
    error_messages = []
    #print_net_constraints()

    # Do until not changed
    changes = 1
    while changes > 0:

        # Reset changed flag
        changes = 0

        # Do for each parent-child ontology class pair
        for parent_onto_class_uri, children_onto_class_uris in parent_child_class_dict.items():
            parent_class_constraints = net_constraints.get(parent_onto_class_uri)

            # Skip parent class if it does not have a ClassConstraint
            if not isinstance(parent_class_constraints, ClassConstraints):
                continue

            # Identify properties in parent's class constraints
            parent_property_uris = set(parent_class_constraints.property_constraints_dict.keys())

            # Do for each child class
            for child_onto_class_uri in children_onto_class_uris:
                child_class_constraints = net_constraints.get(child_onto_class_uri)

                # If child class has no constrataints at all, inherit from parent and move on to next child
                if child_class_constraints is None:
                    net_constraints[child_onto_class_uri] = parent_class_constraints
                    continue

                # Skip child class is not a ClassConstraint (e.g. it's a DatatypeConstraint)
                if not isinstance(child_class_constraints, ClassConstraints):
                    continue

                # Identify properties in child's class constraints
                child_property_uris = set(child_class_constraints.property_constraints_dict.keys())

                # For properties in both parent and child class constraints
                for property_uri in parent_property_uris.intersection(child_property_uris):
                    #print('{} in both child {} and parent {}'.format(property_uri, child_onto_class_uri, parent_onto_class_uri))

                    # Compute net property constraints
                    parent_property_constraints = parent_class_constraints.get_property_constraints(property_uri)
                    child_property_constraints = child_class_constraints.get_property_constraints(property_uri)
                    merged_property_constraints, errmsgs = child_property_constraints.merge_parent(parent_property_constraints)
                    #print('merged_property_constraints', merged_property_constraints)
                    error_messages.extend(errmsgs)

                    # If net property constraint differs from child's, replace it in child's class constraints
                    if merged_property_constraints != child_property_constraints:
                        child_class_constraints.set_property_constraints(property_uri, merged_property_constraints)
                        #print('set class_constraint', merged_property_constraints)
                        changes += 1
                    else:
                        pass
                        #print('constraint not changed')
                    #print_net_constraints()

                # For properties in parent class constraints but not in child class constraints
                for property_uri in parent_property_uris.difference(child_property_uris):
                    #print('{} in parent {} but not child {}'.format(property_uri, parent_onto_class_uri, child_onto_class_uri))

                    # Add parent's property_constraint to child's class constraints
                    property_constraints = deepcopy(parent_class_constraints.get_property_constraints(property_uri))
                    property_constraints.onto_class_uri = child_onto_class_uri
                    child_class_constraints.set_property_constraints(property_uri, property_constraints)
                    #print('set class_constraint', property_constraints)
                    changes += 1
                    #print_net_constraints()

    # Went thru tree with no changes!   Done!
    return net_constraints, error_messages




def _get_property_ranges(ontospy_property_ranges, ontospy_property_triples):
    '''
    This function belongs in the Ontology class.
    It is implemented outside the Ontology class to facilitate unit testing

    Compute the range for all properties in the ontology.
    Add error message for each property with no or multiple ranges,
       and omit those from the returned property_ranges

    Arguments:
        ontospy_property_ranges   {property_uri:[range_uris]}
        ontospy_property_triples  {property_uri:[triples]}

    Return:
        property_ranges  {property_uri:range_uri|None}
        errmsgs          List of error messages
    '''
    # Start with empty list of error messages
    error_messages = []
    property_ranges = {}

    # Do for all properties in ontospy.all_properties
    for property_uri, range_uris in ontospy_property_ranges.items():
        property_ranges[property_uri] = None

        # If ontospy thinks there are no ranges for this property...
        if not range_uris:

            # If the property has a triple with predicate RDFS.range, this is an unsupported feature
            if RDFS.range in [pred for subj, pred, obj in ontospy_property_triples[property_uri]]:
                error_messages.append(UnsupportedFeature(
                    message='Property has unsupported property type',
                    property_uri = property_uri))
            else:
                error_messages.append(OntologyError(
                    message='Property has no ranges',
                    property_uri = property_uri))
            continue

        # If ontospy thinks there multiple ranges for this property, error message
        if len(range_uris) > 1:
            error_messages.append(OntologyError(
                message='Property has {} ranges {}'.format(
                    len(range_uris),
                    pretty_uris(range_uris)),
                property_uri = property_uri))
            continue

        # If we are here, there is one range.  Add it to return value
        property_ranges[property_uri] = range_uris[0]

    # Return property_ranges and error messages
    return property_ranges, error_messages




def _check_range_consistency(all_constraints, property_ranges):
    '''
    This function belongs in the Ontology class.
    It is implemented outside the Ontology class to facilitate unit testing

    Make sure the property range constraints are consistent with the
    property ranges directly specified in the *-da files.

    Arguments:
        all_constraints   {URIRef(onto_class):ClassConstraints|DatatypeConstraints|None} (ontology.constraints)
        property_ranges   {property_uri:range_uri|None}    (derived from ontospy.all_properties)

    Return:
        List of ErrorMessage objects
    '''
    # Start with empty list of error messages
    error_messages = []

    # Do for all owl property constraints
    for onto_class_uri, constraints in all_constraints.items():

        # We are only checking ClassConstraints for now.
        if not isinstance(constraints, ClassConstraints):
            #error_messages.append(UnsupportedFeature(
            #    message='range consistency check not implemented for {}'.format(type(constraints)),
            #    onto_class_uri=onto_class_uri))
            continue

        # For each property constraint in the class constrain...
        class_constraints = constraints
        for property_uri, property_constraints in class_constraints.property_constraints_dict.items():

            # If property has no range constraint, nothing to check
            if property_constraints.value_range is None:
                continue

            # Make sure property is in onto_property_ranges
            if not property_uri in property_ranges:
                error_messages.append(OntologyError(
                    message='property {} missing from ontology property list'.format(pretty_uri(property_uri)),
                    onto_class_uri=onto_class_uri,
                    property_uri=property_uri))
                continue

            # Get ontospy's opinion of this property's range constraint
            range_uri = property_ranges.get(property_uri)   # could be None

            # Compare the owl property constraint with ontospy's opinion
            if range_uri and range_uri != property_constraints.value_range:
                error_messages.append(OntologyError(
                    message='owl subclass constraint {} does not match explicit property constraint {}'.format(
                        pretty_uri(property_constraints.value_range),
                        pretty_uri(range_uri)),
                    onto_class_uri=onto_class_uri,
                    property_uri=property_uri))

    return error_messages
