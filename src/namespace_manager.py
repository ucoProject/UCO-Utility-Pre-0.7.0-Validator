# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
This module provides a global namespace manager.
This is ONLY used to print URIRefs more conveniently.

Usage:
    print(my_uri.n3(namespace_manager.namespace_manager)
'''
import rdflib
namespace_manager = rdflib.Graph().namespace_manager
namespace_manager.bind('owl', 'http://www.w3.org/2002/07/owl#')   # Add this to the default namespaces


def populate(onto_class_uris):
    '''
    Arguments:
        onto_class_uris   List of ontology class uris (rdflib.term.URIRef objects)

    Action:
        Parse the uri's and add namespaces to namespace_manager
    '''
    # Do for each uri
    for onto_class_uri in onto_class_uris:

        # We only recognize unifiedcybertontology uris.
        if 'unifiedcyberontology' not in onto_class_uri:
            continue

        # Suppose the uri is form http://unifiedcyberontology.org/ontology/core/foo#Bar
        # Split at the #.  The result must be two tokens.
        tokens = onto_class_uri.split('#')        # ('http://unifiedcyberontology.org/core/foo', 'Bar')
        if len(tokens) != 2:
            continue

        # The first token contains the prefix
        prefix = tokens[0] + '#'

        # Split the first token at the last / to find the namespace.  The result should be two tokens.
        subtokens = tokens[0].rsplit('/', 1)  # ('http://unifiedcyberontology.org/core', 'foo')
        if len(subtokens) != 2:
            continue

        # The second token is the name of the namespace
        namespace = subtokens[1]

        # Bind the namespace
        namespace_manager.bind(namespace, prefix)
