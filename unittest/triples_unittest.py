# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

import unittest
from triples import get_spo_dict

class TestTriples(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
                                
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_spo_dict(self):
        triples = [
            ('subject1', 'predicate1', 'object1'),
            ('subject1', 'predicate2', 'object2a'),
            ('subject1', 'predicate2', 'object2b'),
            ('subject1', 'predicate2', 'object2b'),
            ('subject2', 'predicate1', 'object3')
        ]
        spo_dict = get_spo_dict(triples)
        expected_spo_dict = \
            {
                'subject1': {
                    'predicate1': {'object1'},
                    'predicate2': {'object2a', 'object2b'},
                },
                'subject2': {
                    'predicate1': {'object3'}
                }
            }

        import pprint
        pprint.pprint(spo_dict)
        self.assertEqual(spo_dict, expected_spo_dict)



if __name__ == '__main__':
    unittest.main()
