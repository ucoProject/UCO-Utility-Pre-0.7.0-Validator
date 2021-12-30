# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
Toolkit Validator main program

Invocation:
     validate ontology [jsonld_data ...]
'''
import argparse
import json
import os
import sys
import serializer
from ontology import get_ontology
from casedata import get_casedata
from validator import validate
from context import Context

def parse_args(args):
    '''
    Arguments:
        args   argument list, usually sys.argv[1:]

    Return:
        Namespace with these attributes:
            ontology_path    Path to serialized ontology file or directory containing turtle files
            data_filepaths   LIST of paths to serialized data objects or json-ld files
    '''
    parser = argparse.ArgumentParser(
        prog='validate',
        description='Validate json-ld files against an Ontology.')

    # FIRST REQUIRED POSITIONAL ARGUMENT
    parser.add_argument(
        type=str,
        dest='ontology_path',
        help='Path to serialized ontology file or directory containing turtle files.')

    # SUBSEQUENT OPTIONAL POSITIONAL ARGUMENTS
    parser.add_argument(
        type=str,
        dest='data_filepaths',
        nargs='*',
        help='Zero or more paths to json-ld files or serialized data objects.')

    # Parse and return namesapce
    return parser.parse_args(args)


def check_ontology_path(ontology_path):
    '''
    Check that ontology_path is a valid path

    Argument:
        ontology_path    Path to serialized ontology file or directory of turtle files

    Return:
        Error message string
        Empty string if there are no errors
    '''
    # If ontology_path is a file, it should be one of the Toolkit's serialized ontology files
    if os.path.isfile(ontology_path):
        try:
            if serializer.get_identifier(ontology_path) != serializer.ONTOLOGY:
                return '{} is not a serialized ontology file'.format(ontology_path)
        except serializer.DeserializeError:
            return '{} is not a serialized ontology file'.format(ontology_path)
        else:
            return ''

    # If ontology_path is a directory, it should contain at least one .ttl file
    if os.path.isdir(ontology_path):
        filenames = os.listdir(ontology_path)
        for filename in filenames:
            if filename.endswith('.ttl'):
                return ''
        return '{} is a directory that does not contain any turtle files'.format(ontology_path)

    # If it's something else, punt
    return '{} is not a file or a directory'.format(ontology_path)


def check_data_paths(data_paths):
    '''
    Check that all the data_paths are a valid data path

    Argument:
        data_paths    List of zero or more paths to json files or serialized casedata objects

    Return:
        List of error message strings
        Empty list if there are no errors
    '''
    # Start with empty list of bad files
    bad_files = []

    # Do for each data_path
    for path in data_paths:

        # If path is a file, it should be
        # one of the Toolkit's serialized json files or a valid json file
        if os.path.isfile(path):

            # If it's a Toolkit serialized json file, cool.
            try:
                if serializer.get_identifier(path) == serializer.CASEDATA:
                    continue
            except serializer.DeserializeError:
                pass

            # If it's a valid json file, cool.
            try:
                json.load(open(path,mode="r", encoding="utf-8"))
                continue
            except (json.decoder.JSONDecodeError, UnicodeDecodeError):
                pass

            # If it's neither, add to list of bad files
            bad_files.append(path)

        # If it's not a file, add to list of bad files
        else:
            bad_files.append(path)

    # If there are any bad files, construct and return error message
    if len(bad_files) == 0:
        return ''
    if len(bad_files) == 1:
        return '{} is neither a serialized casedata object nor a valid json file.'.format(bad_files[0])
    return 'These are neither a serialized casedata objects nor a valid json files: {}.'.format(bad_files)


def main():
    '''
    Verifier main program
    '''
    # Parse command line
    args = parse_args(sys.argv[1:])

    # Make sure the ontology path exists and looks kosher
    errmsg = check_ontology_path(args.ontology_path)
    if errmsg:
        print(errmsg)
        sys.exit(-1)

    # Make sure the data paths exists and look kosher
    errmsg = check_data_paths(args.data_filepaths)
    if errmsg:
        print(errmsg)
        sys.exit(-1)

    # Load the ontology file and print the error messages
    print('ONTOLOGY {}'.format(args.ontology_path))
    ontology = get_ontology(args.ontology_path)
    context = Context().populate(ontology.bindings)
    for errmsg in ontology.error_messages:
        print(errmsg.format(context))


    # Do for each data file
    for filepath in args.data_filepaths:

        # Validate the data file against the ontology file and print error messages
        print('\n\nVALIDATING {}'.format(filepath))
        case_data = get_casedata(filepath)
        context = Context().populate(case_data.bindings)
        errmsgs = validate(ontology, case_data)
        for errmsg in errmsgs:
            print(errmsg.format(context))

    # Done
    sys.exit(0)


main()
