# NOTICE
# This software was produced for the U.S. Government under contract FA8702-21-C-0001,
# and is subject to the Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007)
# ©2021 The MITRE Corporation. All Rights Reserved.

import unittest
import string
import precondition
import rdflib

class TestPrecondition(unittest.TestCase):

    def _test_generator(self):
        prefix_length = 3
        alphabet = string.ascii_lowercase
        prefixes = set()
        for prefix in precondition.PrefixGenerator(prefix_length, alphabet):
            prefixes.add(prefix)
        self.assertEqual(len(prefixes), len(alphabet)**prefix_length)


    def _test_autogenerate_empty_prefix(self):
        prefix_length = 3
        alphabet = string.ascii_lowercase
        text = '''
         "":  "http://example.org/kb#"
         aaa:  def:  ggghi::
         "something": ":foo"
         "something":":foo"
        '''
        self.assertEqual(precondition.autogenerate_empty_prefix(text, prefix_length, alphabet), 'aab')

    def _test_replace_empty_prefix(self):
        text = '''
         "":  "http://example.org/kb#"
         aaa:  def:  ggghi::
         "something": ":foo"
         "something":":foo"
          "@type": "uco-types:ControlledDictionaryEntry",
        '''
        expected_result = '''
         "PREFIX":  "http://example.org/kb#"
         aaa:  def:  ggghi::
         "something": "PREFIX:foo"
         "something":"PREFIX:foo"
          "@type": "uco-types:ControlledDictionaryEntry",
        '''
        self.assertEqual(precondition.replace_empty_prefix(text, 'PREFIX'), expected_result)


    def _test_embed_line_numbers(self):
        text = '''
         "":  "http://example.org/kb#"
         aaa:  def:  ggghi::
         "something": ":foo"
         "something":":foo"
          "@type": "uco-types:ControlledDictionaryEntry",
        '''
        expected_result = '''
         "":  "http://example.org/kb#"
         aaa:  def:  ggghi::
         "something": ":foo"
         "something":":foo"
          "@type": "uco-types:ControlledDictionaryEntry_LINE_5",
        '''
        self.assertEqual(precondition.embed_line_numbers(text), expected_result)


    def _test_precondition1(self):
        text = '''
         "":  "http://example.org/kb#"
         aaa:  def:  ggghi::
         "something": ":foo"
         "something":":foo"
          "@type": "uco-types:ControlledDictionaryEntry",
        '''
        expected_result = '''
         "aab":  "http://example.org/kb#"
         aaa:  def:  ggghi::
         "something": "aab:foo"
         "something":"aab:foo"
          "@type": "uco-types:ControlledDictionaryEntry_LINE_5",
        '''
        self.assertEqual(precondition.precondition(text), expected_result)

    def _test_precondition2(self):
        text = '''
         "":  "http://example.org/kb#"
         aaa:  def:  ggghi::
         "something": ":foo"
         "something":":foo"
        '''
        expected_result = '''
         "PREFIX":  "http://example.org/kb#"
         aaa:  def:  ggghi::
         "something": "PREFIX:foo"
         "something":"PREFIX:foo"
        '''
        self.assertEqual(precondition.precondition(text, 'PREFIX'), expected_result)

    def _test_precondition_no_empty_prefix(self):
        text = '''
         "baz":  "http://example.org/kb#"
         aaa:  def:  ggghi::
         "something": "baz:foo"
         "something":"baz:foo"
        '''
        self.assertEqual(precondition.precondition(text), text)

    def _test_extract_line_number(self):
        stripped_text, number = precondition.extract_line_number('foo')
        self.assertEqual(stripped_text, 'foo')
        self.assertIsNone(number)
        stripped_text, number = precondition.extract_line_number('foo_LINE_123')
        self.assertEqual(stripped_text, 'foo')
        self.assertEqual(number, 123)

    def test_postcondition(self):
        graph = rdflib.Graph()
        graph.add((rdflib.term.URIRef('foo1'), rdflib.term.URIRef('bar'), rdflib.term.URIRef('baz_LINE_42')))
        graph.add((rdflib.term.URIRef('foo2'), rdflib.term.URIRef('bar'), 
                   rdflib.term.Literal('hi', datatype=rdflib.term.URIRef('xsd:string_LINE_82'))))
        graph.add((rdflib.term.URIRef('foo3'), rdflib.term.URIRef('bar'), rdflib.term.Literal('ho')))
        graph.add((rdflib.term.URIRef('foo4'), rdflib.term.URIRef('bar'), rdflib.term.Literal('abc:ho')))
        graph.add((rdflib.term.URIRef('foo5'), rdflib.term.URIRef('bar'), rdflib.term.Literal('abc:ho_LINE_122')))
        graph.add((rdflib.term.URIRef('foo6'), rdflib.term.URIRef('bar'), 
                   rdflib.term.Literal('hi', datatype=rdflib.term.URIRef('xsd:string'))))
        context = {'ho':'http://hohoho#', 'abc':'http://abc#'}
        graph, line_numbers = precondition.postcondition(graph, context)
        self.assertEqual(line_numbers, {
            rdflib.term.URIRef('foo1'): 42,
            rdflib.term.URIRef('foo2'): 82,
            rdflib.term.URIRef('foo5'): 122})
        self.assertEqual(
            list(graph.triples((rdflib.term.URIRef('foo1'), None, None)))[0],
            (rdflib.term.URIRef('foo1'), rdflib.term.URIRef('bar'), rdflib.term.URIRef('baz')))
        self.assertEqual(
            list(graph.triples((rdflib.term.URIRef('foo2'), None, None)))[0],
            (rdflib.term.URIRef('foo2'), rdflib.term.URIRef('bar'), rdflib.term.Literal('hi', datatype=rdflib.term.URIRef('xsd:string'))))
        self.assertEqual(
            list(graph.triples((rdflib.term.URIRef('foo3'), None, None)))[0],
            (rdflib.term.URIRef('foo3'), rdflib.term.URIRef('bar'), rdflib.term.Literal('ho')))
        self.assertEqual(
            list(graph.triples((rdflib.term.URIRef('foo4'), None, None)))[0],
            (rdflib.term.URIRef('foo4'), rdflib.term.URIRef('bar'), rdflib.term.URIRef('http://abc#ho')))
        self.assertEqual(
            list(graph.triples((rdflib.term.URIRef('foo5'), None, None)))[0],
            (rdflib.term.URIRef('foo5'), rdflib.term.URIRef('bar'), rdflib.term.URIRef('http://abc#ho')))
        self.assertEqual(
            list(graph.triples((rdflib.term.URIRef('foo6'), None, None)))[0],
            (rdflib.term.URIRef('foo6'), rdflib.term.URIRef('bar'), rdflib.term.Literal('hi', datatype=rdflib.term.URIRef('xsd:string'))))
            
        #print(line_numbers)
        #for subject, predicate, obj in graph.triples((None, None, None)):
        #    print(repr(subject))
        #    print(repr(predicate))
        #    print(repr(obj))
        #    print()






if __name__ == '__main__':
    unittest.main()
