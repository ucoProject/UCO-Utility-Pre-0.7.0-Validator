# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
Toolkit Describe main program

Invocation:
    describe  serialized_filepath
'''
import argparse
import os
import sys
import serializer

def parse_args(args):
    '''
    Arguments:
        args   argument list, usually sys.argv[1:]

    Return:
        Namespace with these attributes:
            filepath     Full path to serialized ontology or json-ld file
    '''
    parser = argparse.ArgumentParser(
        prog='describe',
        description='Describe serialized filepath.')


    # REQUIRED INPUT PATH
    parser.add_argument(
        type=str,
        action='store',
        dest='filepath',
        help='Full path serialized ontology or json-ld file.')

    # Parse and return namespace
    return parser.parse_args(args)



def main():
    '''
    Describe main program
    '''
    # Parse command line
    args = parse_args(sys.argv[1:])
    filepath = args.filepath

    # Make sure file exists
    if not os.path.exists(filepath):
        print('{}: no such file'.format(filepath))
        sys.exit(-1)

    if not os.path.isfile(filepath):
        print('{} is not a file'.format(filepath))
        sys.exit(-1)

    # Deserialize the metadata
    try:
        metadata = serializer.get_metadata(filepath)
    except serializer.DeserializeError as exc:
        print(exc)
        sys.exit(-1)

    # Print the metadata
    comment = metadata.pop('comment')
    print(comment.strip())
    print()

    version = metadata.pop('version')
    print('Toolkit version: {}'.format(version))

    timestamp = metadata.pop('timestamp')
    print('Build time: {}'.format(timestamp))

    path = metadata.pop('path')
    print('Original source location: {}'.format(path))

    md5 = metadata.pop('md5')
    print('Source md5: {}'.format(md5))

    manifest = metadata.pop('manifest', None)
    if manifest:
        print('Component md5s:')
        for filename, md5 in manifest.items():
            print('    {}  {}'.format(md5, filename))

    # Done
    sys.exit(0)


main()
