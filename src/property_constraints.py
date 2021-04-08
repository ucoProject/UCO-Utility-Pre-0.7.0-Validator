# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
A PropertyConstraints object describes type and cardinality constraints
for a single property of a single ontology class.

This module implements the PropertyConstraints object
'''
from message import OntologyError
from context import Context

class PropertyConstraints:
    '''
    Instances of this class describe the type and cardinality constraints
    for a property of an ontology class.

    This class facilitates collecting the constraints and checking them
    for consistency.

    Attributes:
        onto_class_uri   An rdflib.term.URIRef object for the ontology class or None
        property_uri     An rdflib.term.URIRef object or None
        min_cardinality  An integer or None
        max_cardinality  An integer or None
        value_range      An rdflib.term.URIRef object
        _qualified       A boolean, or None

    Two PropertyConstraint instances are equal if their attributes,
    not including _qualified, are equal.
    '''
    def __init__(self, onto_class_uri=None, property_uri=None):
        '''
        Create and initialize an instance of this class
        The arguments are for error messages and self-description.

        Arguments:
            onto_class_uri  An rdflib.term.URIRef for the ontology class whose
                               property is constrained by these PropertyConstraints
            property_uri    An rdflib.term.URIRef object for the property constrained by these PropertyConstraints
        '''
        self.onto_class_uri = onto_class_uri
        self.property_uri = property_uri
        self.min_cardinality = None
        self.max_cardinality = None
        self.value_range = None
        self._qualified = None     # True/False/None where None means unset

    def add_min_cardinality(self, min_cardinality):
        '''
        "Add" specified min_cardinality value if possible.

        Arguments:
            min_cardinality    The minimum cardinality, an integer

        Return:
            List of ErrorMessages on failure, empty list on success.
        '''
        error_messages = []

        if self._qualified is None:
            self._qualified = False
        elif self._qualified is True:
            error_messages.append(self._get_ontology_error('unqualified min_cardinality specified for a qualified constraint'))

        if self.min_cardinality is None:
            if self.max_cardinality is not None and min_cardinality > self.max_cardinality:
                error_messages.append(self._get_ontology_error('min_cardinality exceeds max_cardinality'))
            else:
                self.min_cardinality = min_cardinality
        elif self.min_cardinality != min_cardinality:
            error_messages.append(self._get_ontology_error('multiple min_cardinality values specified'))

        return error_messages


    def add_max_cardinality(self, max_cardinality):
        '''
        "Add" specified max_cardinality value if possible.

        Arguments:
            max_cardinality    The maximum cardinality, an integer

        Return:
            List of ErrorMessages on failure, empty list on success.
        '''
        error_messages = []

        if self._qualified is None:
            self._qualified = False
        elif self._qualified is True:
            error_messages.append(self._get_ontology_error('unqualified max_cardinality specified for a qualified constraint'))

        if self.max_cardinality is None:
            if self.min_cardinality is not None and max_cardinality < self.min_cardinality:
                error_messages.append(self._get_ontology_error('max_cardinality exceeds min_cardinality'))
            else:
                self.max_cardinality = max_cardinality
        elif self.max_cardinality != max_cardinality:
            error_messages.append(self._get_ontology_error('multiple max_cardinality values specified'))

        return error_messages


    def add_cardinality(self, cardinality):
        '''
        "Add" specified cardinaltiy to self if possible.

        Arguments:
            cardinality    The (minimum and maximum) cardinality, an integer

        Return:
            List of ErrorMessages on failure, empty list on success.
        '''
        error_messages = []

        if self._qualified is None:
            self._qualified = False
        elif self._qualified is True:
            error_messages.append(self._get_ontology_error('unqualified cardinality specified for a qualified constraint'))

        if self.min_cardinality is None and self.max_cardinality is None:
            self.min_cardinality = cardinality
            self.max_cardinality = cardinality
        elif self.min_cardinality != cardinality or self.max_cardinality != cardinality:
            error_messages.append(self._get_ontology_error('multiple cardinality values specified'))

        return error_messages


    def add_qualified_min_cardinality(self, min_cardinality):
        '''
        "Add" specified min_qualified_cardinaltiy value if possible.

        Arguments:
            min_cardinality    The minimum qualified cardinality, an integer

        Return:
            List of ErrorMessages on failure, empty list on success.
        '''
        error_messages = []

        if self._qualified is None:
            self._qualified = True
        elif self._qualified is False:
            error_messages.append(self._get_ontology_error('qualified min_cardinality specified for a unqualified constraint'))

        if self.min_cardinality is None:
            if self.max_cardinality is not None and min_cardinality > self.max_cardinality:
                error_messages.append(self._get_ontology_error('min_cardinality exceeds max_cardinality'))
            else:
                self.min_cardinality = min_cardinality
        elif self.min_cardinality != min_cardinality:
            error_messages.append(self._get_ontology_error('multiple min_cardinality values specified'))

        return error_messages


    def add_qualified_max_cardinality(self, max_cardinality):
        '''
        "Add" specified max_qualified_cardinaltiy value if possible.

        Arguments:
            max_cardinality    The maximum qualified cardinality, an integer

        Return:
            List of ErrorMessages on failure, empty list on success.
        '''
        error_messages = []

        if self._qualified is None:
            self._qualified = True
        elif self._qualified is False:
            error_messages.append(self._get_ontology_error('qualified max_cardinality specified for a unqualified constraint'))

        if self.max_cardinality is None:
            if self.min_cardinality is not None and max_cardinality < self.min_cardinality:
                error_messages.append(self._get_ontology_error('max_cardinality exceeds min_cardinality'))
            else:
                self.max_cardinality = max_cardinality
        elif self.max_cardinality != max_cardinality:
            error_messages.append(self._get_ontology_error('multiple max_cardinality values specified'))

        return error_messages


    def add_qualified_cardinality(self, cardinality):
        '''
        "Add" specified qualified_cardinality to self if possible.

        Arguments:
            cardinality    The (minimum and maximum) qualified cardinality, an integer

        Return:
            List of ErrorMessages on failure, empty list on success.
        '''
        error_messages = []

        if self._qualified is None:
            self._qualified = True
        elif self._qualified is False:
            error_messages.append(self._get_ontology_error('qualified cardinality specified for a qualified constraint'))

        if self.min_cardinality is None and self.max_cardinality is None:
            self.min_cardinality = cardinality
            self.max_cardinality = cardinality
        elif self.min_cardinality != cardinality or self.max_cardinality != cardinality:
            error_messages.append(self._get_ontology_error('multiple cardinality values specified'))

        return error_messages



    def add_value_range(self, value_range):
        '''
        Add specified value_range (usually xsd) value if possible.

        Arguments:
            value_range   The rdflib.term.URIRef of the range type

        Return:
            List of ErrorMessages on failure, empty list on success.
        '''
        error_messages = []

        if self.value_range is None:
            self.value_range = value_range
        else:
            error_messages.append(self._get_ontology_error('multiple ranges specified'))

        return error_messages


    def merge_parent(self, parent):
        '''
        Arguments:
            parent   Another PropertyConstraints object, presumable belonging to a parent class

        Return:
            A tuple consisting of two items:
               A new PropertyConstraints object containing the result of the merger
               A (hopefully empty) list of ErrorMessage objects

        Side effects:
            None.  Self is not changed.

        Definitions and Algorithm:
            Each PropertyConstraint object has three attributes of interest: min_cardinality, max_cardinality, and range.
            If any of these attributes is None, that means it has not been set; there is no default value.

            Before the merge operation, self's constraints must be equal to or tighter than parent's.
            If the parent's constraint is tighter, the offending attibutes are ignored and we get an ErrorMessage.

            The merge operation builds the new merged PropertyConstraints object as follows:
                1. Start with an empty merged PropertyConstraints object and an empty list of ErrorMessages
                2. Copy attributes from self or parent to merged as follows:
                    a. If an attribute is unset (None) in self
                           merged attribute is parent's value (which could also be None)
                    b. If an attribute has a value in self and is unset (None) in parent,
                           merged attribute is self's value
                    c. If an attribute has a value in self and a value in parent.
                           merged attribute is self's value (because self's value should be at least as tight as parent's)
                           if parent's constraint is tighter than or equal to parent's, add ErrorMessage
                3. If both min_cardinality and max_cardinality have values in merged PropertyConstraints,
                    If min_cardinality > max_cardinality, add ErrorMessage and revert to unmerged values.

            The _qualified attribute in the merged constraints is not used.
        '''
        # Step 1.  Initialize.
        merged = PropertyConstraints(onto_class_uri=self.onto_class_uri, property_uri=self.property_uri)
        error_messages = []

        # Step 2 for min_cardinality.
        merged.min_cardinality = parent.min_cardinality if self.min_cardinality is None else self.min_cardinality
        if parent.min_cardinality is not None and self.min_cardinality is not None:
            if parent.min_cardinality > self.min_cardinality:  # parent has tighter constraint
                error_messages.append(self._get_ontology_error(
                    'cannot merge min_cardinality {} with {} from {}'.format(
                        self.min_cardinality, parent.min_cardinality, parent.onto_class_uri)))

        # Step 2 for max_cardinality.
        merged.max_cardinality = parent.max_cardinality if self.max_cardinality is None else self.max_cardinality
        if parent.max_cardinality is not None and self.max_cardinality is not None:
            if parent.max_cardinality < self.max_cardinality:  # parent has tighter constraint
                error_messages.append(self._get_ontology_error(
                    'cannot merge max_cardinality {} with {} from {}'.format(
                        self.max_cardinality, parent.max_cardinality, parent.onto_class_uri)))

        # Step 2 for range.
        merged.value_range = parent.value_range if self.value_range is None else self.value_range
        if parent.value_range is not None and self.value_range is not None:
            if parent.value_range != self.value_range:        # inconsistant ranges (we don't check for subclass yet)
                error_messages.append(self._get_ontology_error(
                    'cannot merge value_range {} with {} from {}'.format(
                        self.value_range, parent.value_range, parent.onto_class_uri)))

        # Step 3.  Make sure min <= max
        if merged.min_cardinality is not None and merged.max_cardinality is not None:
            if merged.min_cardinality > merged.max_cardinality:
                error_messages.append(self._get_ontology_error(
                    'cannot merge cardinalities from {} because min_cardinality exceeds max_cardinality'.format(parent.onto_class_uri)))
                merged.min_cardinality = self.min_cardinality
                merged.max_cardinality = self.max_cardinality

        # Return merged PropertyConstraints and List of error messages
        #print('child  {}\nparent {}\nmerged {} {}'.format(self, parent, merged, error_messages))
        return merged, error_messages



    def check_consistency(self):
        '''
        Check this PropertyConstraints object for global inconsistencies
        that could not be determined when adding items one at a time.

        Return:
            List of ErrorMessages if inconsistencies were found, empty list if not.
        '''
        error_messages = []

        if self._qualified is True:
            if self.value_range is None:
                error_messages.append(self._get_ontology_error('qualified constraint has no range'))
        if self._qualified is False:
            if self.value_range is not None:
                error_messages.append(self._get_ontology_error('unqualified constraint has range'))
        # if self._qualified is None:
        #    pass

        return error_messages


    def describe(self, context=None):
        '''
        Assemble and return a plain-text description of these PropertyConstraints

        Return:
            A single-line string describing this PropertyConstraints object.
        '''
        value = lambda n: 'value' if n == 1 else 'values'
        phrases = []
        if context is None:
            context = Context()
        if self.onto_class_uri:
            phrases.append('Class {}'.format(context.format(self.onto_class_uri)))
        if self.property_uri:
            phrases.append('Property {}'.format(context.format(self.property_uri)))
        else:
            phrases.append('Property')

        if self.max_cardinality == 0:
            phrases.append('may have no values')
        elif self.min_cardinality in (None, 0):
            if self.max_cardinality is None:
                phrases.append('may have any number of values')
            else: # self.max_cardinality > 0
                phrases.append('may have at most {} {}'.format(self.max_cardinality, value(self.max_cardinality)))
        else:  # self.min_cardinality > 0
            if self.max_cardinality is None:
                phrases.append('must have at least {} {}'.format(self.min_cardinality, value(self.min_cardinality)))
            elif self.min_cardinality == self.max_cardinality:
                phrases.append('must have exactly {} {}'.format(self.min_cardinality, value(self.min_cardinality)))
            else:  # self.max_cardinality > 0
                phrases.append('must have between {} and {} values'.format(self.min_cardinality, self.max_cardinality))

        if self.value_range:
            phrases.append('of type {}'.format(self.value_range))

        return ' '.join(phrases)

    def _get_ontology_error(self, message):
        '''
        Arguments:
            message  A message string describing some kind of error condition
        Return:
            An OntologyError object using self.onto_class_uri and self.property_uri with the message
        '''
        return OntologyError(
            message='constraint violation: ' + message,
            onto_class_uri=self.onto_class_uri,
            property_uri=self.property_uri)

    def __members(self):
        '''
        Two instances of this class are equal if the __member attributes are equal
        '''
        return (self.onto_class_uri, self.property_uri, self.min_cardinality, self.max_cardinality, self.value_range)


    def __str__(self):
        return '<{} {} [{}-{}] {}>'.format(
            self.onto_class_uri if self.onto_class_uri else None,
            self.property_uri if self.property_uri else 'DATATYPE',
            '?' if self.min_cardinality is None else self.min_cardinality,
            '?' if self.max_cardinality is None else self.max_cardinality,
            self.value_range if self.value_range else '?')

    def __eq__(self, other):
        '''
        Two instances of this class are equal if the __member attributes are equal
        '''
        if type(other) is type(self):
            return self.__members() == other.__members()
        else:
            return False

    def __hash__(self):
        '''
        Two instances of this class are equal if the __member attributes are equal
        '''
        return hash(self.__members())
