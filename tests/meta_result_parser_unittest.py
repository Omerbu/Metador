"""Unittest for meta_result_parser module.

Requires test files (I.E music files) to function.

"""
import unittest
import metacore
from meta_result_parser import ResultParser


class TestMetaResultParser(unittest.TestCase):

    def test_result_parser_basic(self):     # To include multiple test files.
        results_gen, org_duration = metacore.fingerprint_search(
            "test_files/lll.m4a")
        result_parser = ResultParser(results_gen, org_duration)
        best_result = result_parser.main()
        # self.assertEqual(best_result, (u'Arctic Monkeys', u'Do I Wanna Know?'))
        print best_result


if __name__ == '__main__':
    unittest.main()
