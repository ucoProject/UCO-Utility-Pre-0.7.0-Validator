# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

import os
import unittest
import casedata
import serializer

class TestCasedata(unittest.TestCase):

    def setUp(self):
        self.this_dirpath = os.path.dirname(os.path.abspath(__file__))
        self.output_dirpath = os.path.join(self.this_dirpath, 'testdata', 'tmp')
        self.input_dirpath = os.path.join(self.this_dirpath, 'testdata', 'casedata')

    def tearDown(self):
        for filename in os.listdir(self.output_dirpath):
            os.remove(os.path.join(self.output_dirpath, filename))

    def test_get_casedata(self):
        c = casedata.get_casedata(os.path.join(self.input_dirpath, 'Oresteia.json'))

    def test_write_preconditioned_file(self):
        c = casedata.get_casedata(
            path=os.path.join(self.input_dirpath, 'Oresteia.json'),
            output_filepath=os.path.join(self.input_dirpath, 'Oresteia_preconditioned.json'))

    def test_serialize(self):
        c = casedata.get_casedata(
            path=os.path.join(self.input_dirpath, 'Oresteia.json'),
            verbose=False)

        serialized_filepath = os.path.join(self.output_dirpath, 'serialized.pkl')
        c.serialize(serialized_filepath, 'This is a test')

        c1 = casedata.get_casedata(serialized_filepath)
        self.assertEqual(c.__dict__, c1.__dict__)

    def test_all_data(self):
        for filename in self.input_dirpath:
            if filename.endswith('.json'):
                filepath = os.path.join(json_dirpath, filename)
                print('Building {}'.format(filepath))
                c = casedata.get_casedata(filepath)



if __name__ == '__main__':
    unittest.main()
