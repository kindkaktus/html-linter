#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import unittest

sys.path.append("..")
from html_validator import validate


class ValidationTestCase(unittest.TestCase):

    def test_validate_good_html_document(self):
        self.assertTrue(validate('http://www.ibooksmart.com')['status'])

    def test_validate_bad_html_document(self):
        result = validate('http://blog.tjll.net/ssh-kung-fu/')
        self.assertFalse(result['status'])
        self.assertGreater(len(result['error']), 0)

if __name__ == '__main__':
    unittest.main()
