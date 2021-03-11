# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
Toolkit Serializer main program

Invocation:
    serialize [-o output_path] [-c comments] path

    where path is one of these:
        ontology: Full path to a directory containing turtle files
        jsonld:   Full path to a json-ld file
'''
import argparse
import os
import sys
from ontology import get_ontology
from casedata import get_casedata

def parse_args(args):
    '''
    Arguments:
        args   argument list, usually sys.argv[1:]

    Return:
        Namespace with these attributes:
            output_path   The output path, or None if not specified
            input_path    The ontology or jsonld file to serialize
            comments      Description to include in the serialized file, or None to prompt
    '''
    parser = argparse.ArgumentParser(
        prog='serialize',
        description='Serialize json-ld file or ontology directory.')

    # OPTIONAL OUTPUT PATH
    parser.add_argument(
        '-o',
        type=str,
        required=False,
        default=None,
        action='store',
        dest='output_path',
        help='Full path to output serialized file.  Default is input_path.pkl')

    # OPTIONAL COMMENT STRING
    parser.add_argument(
        '-c',
        type=str,
        required=False,
        default=None,
        action='store',
        dest='comments',
        help='Description to be stored in the serialized file. Will read from stdin if omitted.')


    # REQUIRED INPUT PATH
    parser.add_argument(
        type=str,
        action='store',
        dest='input_path',
        help='Full path to json-ld file or ontology directory to serialized.')

    # Parse and return namespace
    return parser.parse_args(args)



def main():
    '''
    Serializer main program
    '''
    # Parse command line
    args = parse_args(sys.argv[1:])

    # Make sure input_path exists.  If it's a directory, make sure it has turtle files.
    input_path = args.input_path
    if os.path.isfile(input_path):
        pass
    elif os.path.isdir(input_path):
        filenames = os.listdir(input_path)
        for filename in filenames:
            if filename.endswith('.ttl'):
                break
        else:
            print('{} is a directory with no turtle files'.format(input_path))
            sys.exit(-1)
    else:
        print('{} is neither a file nor a directory'.format(args.input_path))
        sys.exit(-1)


    # Make sure output_path is specified.  If not, use default
    output_path = args.output_path
    if not output_path:
        output_path = input_path + '.pkl'

    # Make sure comment is specified.  If not, prompt and read from stdin.
    comments = args.comments
    if not comments:
        print('Enter description, terminate with return + ctrl-d')
        comments = sys.stdin.read()   # Could be redirected from a file


    # If path is a file, serialize json-ld file
    if os.path.isfile(input_path):
        print('Serializing json-ld file {} -> {}'.format(input_path, output_path))
        try:
            casedata = get_casedata(input_path)
            casedata.serialize(output_path, comments)
        except Exception as exc:
            print(exc)
            sys.exit(-1)

    # If path is a directory, serialize ontology
    if os.path.isdir(args.input_path):
        print('Serializing ontology in directory {} -> {}'.format(input_path, output_path))
        try:
            ontology = get_ontology(input_path)
            ontology.serialize(output_path, comments)
        except Exception as exc:
            print(exc)
            sys.exit(-1)

    # Done
    sys.exit(0)


main()
