# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

import os
import unittest
import message

class TestMessage(unittest.TestCase):

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

    def test_equivalence(self):
        e1 = message.UnsupportedFeature(message='foo', line_number=73)
        e2 = message.UnsupportedFeature(message='foo', line_number=73)
        self.assertEqual(e1, e2)
        s = {e1, e2}
        self.assertEqual(len(s), 1)

    def test_non_equivalence(self):
        e1 = message.UnsupportedFeature(message='foo', line_number=73)
        e2 = message.ConstraintError(message='foo', line_number=73)
        e3 = message.UnsupportedFeature(message='foo', line_number=743)
        self.assertNotEqual(e1, e2)
        self.assertNotEqual(e1, e3)
        self.assertNotEqual(e2, e3)
        s = {e1, e2, e3}
        self.assertEqual(len(s), 3)

if __name__ == '__main__':
    unittest.main()
