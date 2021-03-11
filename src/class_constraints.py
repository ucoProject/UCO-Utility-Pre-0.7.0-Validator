# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
This module manages ontology class constraints.
'''
import rdflib
from rdflib.namespace import OWL, RDF
from property_constraints import PropertyConstraints
from message import OntologyError, UnsupportedFeature
from message import pretty_uri
from triples import get_spo_dict



def get_class_constraints(onto_class_uri, triples):
    '''
    Build and return a ClassConstraints object for the specified list of triples

    Arguments:
        onto_class_uri   A rdflib.term.URIRef of the source ontology class (used ONLY for building messages)
        triples          A list of triples from an ontospy.core.entities.OntoClass (e.g. onto_class.triples)

    Return:
        A tuple (ClassConstraints object, LIST of ErrorMessage objects)
    '''
    # Create empty ClassConstraints object and empty list of ErrorMessages
    class_constraints = ClassConstraints(onto_class_uri)
    error_messages = []

    # Convert list of triples to {subject:{predicate:{objects}}}
    spo_dict = get_spo_dict(triples)

    # Do for each node...
    for subject, po_dict in spo_dict.items():

        # Skip this node if it is the parent node
        if not isinstance(subject, rdflib.term.BNode):
            continue

        # If we're here, then subject is a BNode
        # Remove and report predicates with multiple objects for this BNode
        # Sets of a single object by that single object.
        for predicate in set(po_dict.keys()):
            objects = po_dict[predicate]
            if len(objects) > 1:
                error_messages.append(OntologyError(
                    message = 'conflicting specification of {} as {}'.format(predicate, objects),
                    onto_class_uri = onto_class_uri,
                    property_uri = po_dict.get(OWL.onProperty)))
                po_dict.pop(predicate)          # remove predicate and its multiple object from dictionary
            else:
                po_dict[predicate] = objects.pop()  # replace set of one object by the one object


        # Now po_dict maps predicates to single objects: {predicate:object}
        # Get RDF.type and onProperty for this BNode
        constraints_type = po_dict.get(RDF.type)
        property_uri = po_dict.get(OWL.onProperty)

        # Skip this BNode if its RDF.type is not OWL.Restriction
        if constraints_type != OWL.Restriction:
            error_messages.append(UnsupportedFeature(
                onto_class_uri = onto_class_uri,
                property_uri = property_uri,
                message='unsupported constraints type {}'.format(constraints_type)))
            continue

        # Skip this BNode if its OWL.onProperty is missing
        if not property_uri:
            error_messages.append(OntologyError(
                onto_class_uri = onto_class_uri,
                message='constraints has no property value'))
            continue

        # Create empty PropertyConstraints object and attach to property in Constraints object
        property_constraints = PropertyConstraints(onto_class_uri, property_uri)
        class_constraints.set_property_constraints(property_uri, property_constraints)

        # Do for each predicate
        for predicate, obj in po_dict.items():

            # Skip RDF.type and OWL.onProperty because we already accounted for them
            if predicate in (RDF.type, OWL.onProperty):
                continue

            # Populate property_constraints depending on the predicate and its value
            if predicate == OWL.onDataRange:
                error_messages.extend(property_constraints.add_value_range(obj))
            elif predicate == OWL.onClass:
                error_messages.extend(property_constraints.add_value_range(obj))
            elif predicate == OWL.minCardinality:
                error_messages.extend(property_constraints.add_min_cardinality(int(obj.value)))
            elif predicate == OWL.maxCardinality:
                error_messages.extend(property_constraints.add_max_cardinality(int(obj.value)))
            elif predicate == OWL.cardinality:
                error_messages.extend(property_constraints.add_cardinality(int(obj.value)))
            elif predicate == OWL.minQualifiedCardinality:
                error_messages.extend(property_constraints.add_qualified_min_cardinality(int(obj.value)))
            elif predicate == OWL.maxQualifiedCardinality:
                error_messages.extend(property_constraints.add_qualified_max_cardinality(int(obj.value)))
            elif predicate == OWL.qualifiedCardinality:
                error_messages.extend(property_constraints.add_qualified_cardinality(int(obj.value)))
            else:
                error_messages.append(UnsupportedFeature(
                    message = 'unsupported predicate {}'.format(predicate),
                    onto_class_uri = onto_class_uri,
                    property_uri = property_uri))

        # Check property constraints for consistency
        error_messages.extend(property_constraints.check_consistency())

    # Return the Constraints object and the ErrorMessages
    return class_constraints, error_messages



class ClassConstraints:
    '''
    This class manages a set of PropertyConstraints objects.

    Attributes:
        onto_class_uri            A URIRef of the source ontology class (used ONLY for building messages)
        property_constraints_dict Maps property IRI to set of PropertyConstraints objects {property:{PropertyConstraints}}
    '''
    def __init__(self, onto_class_uri):
        '''
        Create and initialize an instance of this class

        Arguments:
            onto_class_uri    URIRef of the ontology class constrained by these class_constraints (for errmsgs only)
        '''
        self.onto_class_uri = onto_class_uri
        self.property_constraints_dict = {}         # {property_uri:PropertyConstraints}

    def __str__(self):
        if self.property_constraints_dict:
            return '\n'.join([str(property_constraints) for property_constraints in self.property_constraints_dict.values()])
        else:
            return '<Empty>'

    def set_property_constraints(self, property_uri, property_constraints):
        '''
        Attach Contraint object to specified property_uri.
        If PropertyConstraints object already exists for this property, clobber it.

        Arguments:
            property_uri          The URIRef for the property to attach the property_constraints to
            property_constraints  A PropertyConstraints object
        '''
        self.property_constraints_dict[property_uri] = property_constraints


    def get_property_constraints(self, property_uri):
        '''
        Return the Constraints object attached to the specified property_uri

        Arguments:
            property_uri   The URIRef for the property whose Constraints to retrieve

        Return:
            The PropertyConstraints object, or None if there's no such property_uri
        '''
        return self.property_constraints_dict.get(property_uri)


    def get_forbidden_properties(self):
        '''
        Return:
            A set of property_uris for forbidden properties.  These properties have max_cardinality 0
        '''
        forbidden_properties = set()
        for property_uri, property_constraints in self.property_constraints_dict.items():
            if property_constraints.max_cardinality is not None and property_constraints.max_cardinality == 0:
                forbidden_properties.add(property_uri)
        return forbidden_properties


    def get_required_properties(self):
        '''
        Return:
            A set of property_uris for required properties.  These properties have min_cardinality > 0
        '''
        required_properties = set()
        for property_uri, property_constraints in self.property_constraints_dict.items():
            if property_constraints.min_cardinality is not None and property_constraints.min_cardinality > 0:
                required_properties.add(property_uri)
        return required_properties


    def describe(self):
        '''
        Assemble and return a plain-text description of the class and
        property constraints in this object.
        '''
        lines = []
        for property_constraints in self.property_constraints_dict.values():
            lines.append(property_constraints.describe())
        for required_property in self.get_required_properties():
            lines.append('Class {}: Property {} is required'.format(
                pretty_uri(self.onto_class_uri), required_property))
        for forbidden_property in self.get_forbidden_properties():
            lines.append('Class {}: Property {} is forbidden'.format(
                pretty_uri(self.onto_class_uri), forbidden_property))
        if not lines:
            lines.append('Empty')
        return '\n'.join(lines)
