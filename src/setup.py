# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

from setuptools import setup

setup(
    name='Toolkit',
    version='1.0',
    py_modules = [
        'casedata',
        'class_constraints',
        'datatype_constraints',
        'message',
        'namespace_manager',
        'ontology',
        'precondition',
        'property_constraints',
        'serializer',
        'triples',
        'validator',
        'xsd_validator',
        'validate',
        'serialize',
        'describe',
        'v4_to_v5'
    ],
    install_requires=[
        'lxml',
        'ontospy',
        'rdflib'
    ],
    entry_points='''
        [console_scripts]
        validate=validate:main
        describe=describe:main
        serialize=serialize:main
        v4to5=v4_to_v5:main
    '''
)
