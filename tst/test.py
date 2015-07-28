#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import unittest

sys.path.append("..")
from html_validator import validate


class ValidationTestCase(unittest.TestCase):

    def test_validate_good_html_document(self):
        errors = validate('http://www.ibooksmart.com')
        self.assertEquals(len(errors), 0)

    def test_validate_bad_html_document(self):
        errors = validate('http://blog.tjll.net/ssh-kung-fu/')
        self.assertGreater(len(errors), 0)

if __name__ == '__main__':
    unittest.main()
