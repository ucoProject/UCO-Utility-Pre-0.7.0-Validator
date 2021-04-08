# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
This module implements the CaseData object.

An instance of this object contains the rdflib.Graph and metadata
derivied from preconditioning a json-ld file and applying Ontospy to it.
'''
import datetime
import json
import os
import tempfile
from ontospy import Ontospy
import serializer
from precondition import precondition, postcondition
from context import Context

VERSION = '1.1'   # Appears in the metadata when serialized

def get_casedata(path, output_filepath=None, verbose=False, **kwargs):
    '''
    If path is a serialized casedata file, deserialize it and return it.
    If path is file containing valid json-ld, ingest it.
    If path is file that is contains something else, raise exception.
    If path is a directory or something else, raise exception.

    Arguments:
        path             Full path to a serialized casedata file or a json-ld file
        output_filepath  If specified and using Ontospy, filepath to save preconditioned file
        verbose          If true and using Ontospy, Ontospy library runs verbosely
        kwargs           Additional arguments passed on to Ontospy

    Return:
        An CaseData object

    Raise:
        Exception if path is not a serialized casedata file or a valid json-ld file.
    '''
    # Start with an empty CaseData object
    casedata = CaseData()

    # If path is not a file, raise
    if not os.path.isfile(path):
        raise Exception('{} is neither a serialized casedata file nor a jsonld file'.format(path))

    # If path is a serialized casedata file, deserialize it and return casedata
    try:
        identifier, metadata, casedata.__dict__ = serializer.deserialize(path)
        if identifier == serializer.CASEDATA:
            if metadata['version'] != VERSION:
                print('{} was serialized with a different version of the toolkit.  Use this command to reserialize:'.format(path))
                print()
                print('    serialize {}'.format(metadata['path']))
                print()
                raise Exception('{} was serialized with a different version of the toolkit.'.format(path))
            return casedata
    except serializer.DeserializeError:
        pass

    # If it's not a serialized casedata file, assume it contains valid json-ld and ingest it.
    try:
        casedata.__dict__ = _read_jsonld_file(path, output_filepath, verbose, **kwargs)
        return casedata
    except json.decoder.JSONDecodeError as exc:
        raise Exception('{} is not a json file.'.format(path)) from exc

    # Return the casedata object
    return casedata



class CaseData:
    '''
    This class contains information derived from having ontospy ingest json-ld data.

    Attributes:
        jsonld_filepath  The path to the original json-ld file
        graph            Json-ld data decomponsed to an rdflib.Graph of triples
        line_numbers     {node:line_number}, where node is a URIRef or a BNode
    '''
    def __init__(self):
        self.jsonld_filepath = None   # Path to json-ld file
        self.graph = None             # rdflib.Graph of json-ld data
        self.line_numbers = {}        # {node:line_number} where node is a URIRef or a BNode
        self.bindings = []            # [(prefix, uri)] from ontospy.namespaces


    def serialize(self, output_filepath, comment):
        '''
        Serialize this object and write it to the specified output file.

        Argument:
            output_filepath    Full path of file to receive the serialized object
            comment            A comment string to include in the serialized object
        '''
        identifier = serializer.CASEDATA
        file_hash = serializer.get_hash(self.jsonld_filepath)
        metadata = {
            'comment': comment,
            'version': VERSION,
            'path': os.path.abspath(self.jsonld_filepath),
            'timestamp': datetime.datetime.now().isoformat(),
            'md5': file_hash
        }
        serializer.serialize(identifier, metadata, self.__dict__, output_filepath)


def _read_jsonld_file(jsonld_filepath, output_filepath, verbose, **kwargs):
    '''
    Load and parse the json-ld file at jsonld_filepath.
    If output_filepath is specified, save the preconditioned text there (for debugging)

    Arguments:
        jsonld_filepath    Full path to json-ld file
        output_filepath    If not None, filepath to save preconditioned file
        verbose            If true, Ontospy library runs verbosely
        kwargs             Additional arguments passed on to Ontospy

    Return:  dictionary
        {
            'jsonld_filepath':filepath,        # Full path to json-ld file
            'graph':rdflib_graph_obj,          # Json-ld data decomponsed to an rdflib.Graph of triples
            'line_numbers':line_numbers_dict   # {node:line_number}, where node is a URIRef or a BNode
            'bindings':(qualiifer:uri_string)  # List of binding tuples, e.g. ('core', 'http://unifiedcyberontology.org/core')
        }
    '''
    # Read the jsonld file  (could raise exception)
    with open(jsonld_filepath, 'r') as infile:
        text = infile.read()

    # Precondition it
    preconditioned_text = precondition(text)

    # If specified, save text in output_filepath
    if output_filepath:
        with open(output_filepath, 'w') as outfile:
            outfile.write(preconditioned_text)

    # Get rdflib.Graph for preconditioned file
    # ------------------------------------------------------------------
    # This is a workaround for a bug in ontospy that prevents us from inputting the text directly.
    # Write the preconditioned text to a temporary file and let ontospy read it
    # The bug is in line 188 of ontospy/core/rdf_loader.py
    # The line reads:   def load_file(file_obj)
    # It should read:   def load_file(self, file_obj)
    # ------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tempdirname:
        temp_filepath = os.path.join(tempdirname, 'preconditioned.json')
        with open(temp_filepath, 'w') as outfile:
            outfile.write(preconditioned_text)
        ontospy = Ontospy(
            uri_or_path=temp_filepath,
            rdf_format='jsonld',
            verbose=verbose,
            **kwargs)

    graph = ontospy.rdflib_graph
    context = Context().populate(ontospy.namespaces)


    # If ontospy cannot read the file, it prints an error message
    # and returns an object with a zero-length graph
    # Raise an exception
    if not graph:
        raise Exception('Cannot parse graph from {}'.format(jsonld_filepath))

    # Build new graph by remove the embedded line number from ontospy's graph
    # and remember the line numbers in mapping {Node:line_number}
    graph, line_numbers_dict = postcondition(graph, context)

    # Construct and return results
    return {
        'jsonld_filepath':jsonld_filepath,
        'graph':graph,
        'bindings':context.bindings,
        'line_numbers':line_numbers_dict
    }
