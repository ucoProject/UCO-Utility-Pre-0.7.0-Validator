# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
This module implements the case toolkit serialization methods
for serializing ontologies and json-ld data files.

Each serialized file is a binary file that contains three sections:
        The 8-byte identifier ("magic number"): "ontology" or "casedata"
        The python-pickled metadata dictionary
        The python-pickled Ontology or CaseData object

The python-pickled dictionary includes:
        source:      The path to the item that was serialized
        md5:         The md5 of the item that was serialized
        timestamp:   The creation date and time
        description: A user-supplied description

The reason for the metadata is because if there are multiple
serialized file for different versions of data, we can be sure
which one contains which data.

This file structure allows examination of the metadata without
having to read the entire object.
'''
import pickle
import pprint
import hashlib
import os

ONTOLOGY = 'ontology'
CASEDATA = 'casedata'

class DeserializeError(Exception):
    'Exception raised on deserializing a file not serialized by this toolkit'
    pass

def serialize(identifier, metadata, obj, output_filepath):
    '''
    Arguments:
        identifier       Eight-byte filetype (ontology or casedata)
        metadata         Dictionary of metadata (see the module doc block)
        obj              The __dict__ of the Ontology or CaseData object being serialized
        output_filepath  Full path to the output serialized file
    '''
    # Serialize and write
    with open(output_filepath, 'wb') as outfile:
        outfile.write(identifier.encode('ascii'))
        outfile.write(pickle.dumps(metadata))
        outfile.write(pickle.dumps(obj))


def deserialize(serialized_filepath):
    '''
    Arguments:
        serialized_filepath    Full path to input serialized file

    Return:
        3-tuple of (identifier, metadata, obj)

    Raise:
        DeserializeError if file was not serialized by this toolkit.
        other Exception on I/O errors, etc.
    '''
    with open(serialized_filepath, 'rb') as infile:
        identifier = _read_identifier(infile)
        metadata = pickle.load(infile)
        obj = pickle.load(infile)

    return identifier, metadata, obj


def get_metadata(serialized_filepath):
    '''
    Arguments:
        serialized_filepath    Full path to input serialized file

    Return:
        The metadata serialized into this file

    Raise:
        DeserializeError if file was not serialized by this toolkit.
        other Exception on I/O errors, etc.
    '''
    with open(serialized_filepath, 'rb') as infile:
        _identifier = _read_identifier(infile)
        metadata = pickle.load(infile)

    return metadata


def get_identifier(serialized_filepath):
    '''
    Arguments:
        serialized_filepath    Full path to serialized file

    Return:
        identifier    The 8-character file type (ontology or casedata)

    Raise:
        DeserializeError if file was not serialized by this toolkit.
        other Exception on I/O errors, etc.
    '''
    with open(serialized_filepath, 'rb') as infile:
        identifier = _read_identifier(infile)

    return identifier


def describe(serialized_filepath):
    '''
    Arguments:
        serialize_filepath   Full path to serialize file

    Return:
        A multi-line description of the file base on the metadata
    '''
    with open(serialized_filepath, 'rb') as infile:
        identifier = _read_identifier(infile)
        metadata = pickle.load(infile)

    lines = []
    lines.append('{} file'.format(identifier))
    lines.append('')
    comment = metadata.pop('comment', None)
    if comment:
        lines.append(comment)
        lines.append('')
    lines.append(pprint.pformat(metadata))
    return '\n'.join(lines)



def get_hash(filepath):
    '''
    Arguments:
       filepath   Full path to the jsonld data file

    Return:
        The hexlified md5 of the file
    '''
    if not os.path.isfile(filepath):
        raise Exception('filepath {} is not a file'.format(filepath))

    with open(filepath, 'rb') as infile:
        return hashlib.md5(infile.read()).hexdigest()


def get_hash_and_manifest(turtle_dirpath):
    '''
    Arguments:
        turtle_dirpath   Full path to the directory contining ontology turtle (.ttl) files

    Return: Tuple of two items
        The hexlified md5 of the directory
        The manifiest dictionary {filename:hexlified_md5}

    Note:
        The "md5 of the directory" is the md5 of the file that would result from
        concatenating all the .ttl files in the directory in alphabetical order.
    '''
    if not os.path.isdir(turtle_dirpath):
        raise Exception('turtle_dirpath {} is not a directory'.format(turtle_dirpath))

    dirhash = hashlib.md5()
    manifest = {}
    filenames = sorted(os.listdir(turtle_dirpath))

    for filename in filenames:
        if not filename.endswith('.ttl'):
            continue

        filepath = os.path.join(turtle_dirpath, filename)
        if not os.path.isfile(filepath):
            continue

        manifest[filename] = get_hash(filepath)
        with open(filepath, 'rb') as infile:
            dirhash.update(infile.read())

    if not manifest:
        raise Exception('turtle_dirpath {} does not contain any turtle (.ttl) files'.format(turtle_dirpath))

    return dirhash.hexdigest(), manifest


def _read_identifier(infile):
    '''
    Arguments:
        infile   File descriptor for serialized file, opened 'rb'

    Return:
        The eight-character identifier string

    Raise:
       DeserializeError  if file does not contain an expected 8-byte "magic" number
    '''
    # Read eight-byte "magic"
    try:
        identifier = infile.read(8).decode('ascii')
    except UnicodeDecodeError:
        raise DeserializeError('{} was not serialized by this toolkit'.format(infile.name))

    # Make sure "magic" is one of ours
    if identifier not in (ONTOLOGY, CASEDATA):
        raise DeserializeError('{} was not serialized by this toolkit'.format(infile.name))

    # Return "magic" string
    return identifier
