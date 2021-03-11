# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

import os
import unittest
import serializer

# If we want a class that can be pickled, it must be defined statically.
# It can be defined in the TestSerialize class as a class attribute or
# outside the class, but NOT inside the calling function.
class Foo: pass

class TestSerialize(unittest.TestCase):

    def setUp(self):
        self.this_dirpath = os.path.dirname(os.path.abspath(__file__))
        self.output_dirpath = os.path.join(self.this_dirpath, 'testdata', 'tmp')
        self.input_dirpath = os.path.join(self.this_dirpath, 'testdata', 'serializer')

    def tearDown(self):
        for filename in os.listdir(self.output_dirpath):
            os.remove(os.path.join(self.output_dirpath, filename))

    def test_serialize(self):

        # Create an object
        obj = Foo()
        obj.alpha = 'alpha'
        obj.beta = 'beta'

        # Create metadata
        metadata = {
            'meta': 1,
            'data': 2
        }

        # Define file identifier
        identifier = 'ontology'

        # Serialize it
        serialized_filepath = os.path.join(self.output_dirpath, 'test.pkl')
        serializer.serialize(identifier, metadata, obj, serialized_filepath)

        # Deserialize it
        recovered_identifier = serializer.get_identifier(serialized_filepath)
        self.assertEqual(identifier, recovered_identifier)

        recovered_metadata = serializer.get_metadata(serialized_filepath)
        self.assertEqual(metadata, recovered_metadata)

        recovered_identifier, recovered_metadata, recovered_obj = serializer.deserialize(serialized_filepath)
        self.assertEqual(identifier, recovered_identifier)
        self.assertEqual(metadata, recovered_metadata)
        self.assertEqual(vars(obj), vars(recovered_obj))


    def test_bad_serialize(self):

        serialized_filepath = os.path.join(self.output_dirpath, 'test.pkl')
        serializer.serialize('badtype', {}, None, serialized_filepath)

        with self.assertRaises(serializer.DeserializeError):
            recovered_identifier = serializer.get_identifier(serialized_filepath)

        with self.assertRaises(serializer.DeserializeError):
            recovered_metadata = serializer.get_metadata(serialized_filepath)

        with self.assertRaises(serializer.DeserializeError):
            recovered_identifier, recovered_metadata, recovered_obj = serializer.deserialize(serialized_filepath)

    def test_get_hash(self):
        md5 = serializer.get_hash(os.path.join(self.input_dirpath, 'data.json'))
        self.assertEqual(md5, '3998d74ed812aec3a7b9a80973f03046')  # hand-computed value
        
        with self.assertRaises(Exception):
            serializer.get_hash('nosuchfile')

        with self.assertRaises(Exception):
            serializer.get_hash(os.path.join(self.input_dirpath, 'turtledir'))


    def test_get_hash_and_manifest(self):
        md5, manifest = serializer.get_hash_and_manifest(os.path.join(self.input_dirpath, 'turtledir'))
        self.assertEqual(md5, 'ba18483a014754ced37d587e8d100f96')  # hand-computed value
        self.assertEqual(manifest, {
            'curley.ttl':'224408bf4afec85de8f8e39d7c4bb5ed',
            'larry.ttl':'8721b99ad42acfc5ef8ea4ce759f069e',
            'moe.ttl':'70005f7f52039284baf20c1b004905cf'})          # hand-computed values

        with self.assertRaises(Exception):
            serializer.get_hash_and_manifest('nosuchfile')

        with self.assertRaises(Exception):
            serializer.get_hash_and_manifest(os.path.join(self.input_dirpath, 'data.json'))

    def test_describe(self):
        s = serializer.describe(os.path.join(self.input_dirpath, 'serialized_ontology.pkl'))
        print(s)

if __name__ == '__main__':
    unittest.main()
