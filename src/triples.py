# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

'''
This module implements a single function that
converts a list of triples to a dictionary
of {subject:{predicate:{objects}}}

This function is implemented separately so that it can
be used in multiple places
'''
from collections import defaultdict

def get_spo_dict(triples):
    '''
    Arguments:
        triples   A list of triples

    Return:
        {subject:{predictate:{objects}}}

    Note:
        The predicates map to SETS of objects.
    '''
    spo_dict = defaultdict(lambda: defaultdict(set))
    for subject, predicate, obj in triples:
        spo_dict[subject][predicate].add(obj)

    return spo_dict
