import unittest

import sys
import os
import logging

format = ' '.join(['%(asctime)s', '%(levelname)s', '%(module)s', '%(funcName)s', 'L%(lineno)s', '%(message)s'])
logging.basicConfig(stream=sys.stdout, format=format, level=logging.INFO)

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))

from waferslim import execution
from waferslim.tests.fixtures import echo_fixture
from waferslim.import_utils import get_aliases
import waferslim.import_utils


class ConventionsTestCase(unittest.TestCase):
    def test_lower_camel_case(self):
        self.assertEqual(
            waferslim.import_utils.to_lower_camel_case('pythonic_case'),
            'pythonicCase'
        )
        self.assertEqual(
            waferslim.import_utils.to_lower_camel_case('CamelCase'),
            'camelCase'
        )
        self.assertEqual(
            waferslim.import_utils.to_lower_camel_case('camelCase'),
            'camelCase'
        )

    def test_upper_camel_case(self):
        self.assertEqual(
            waferslim.import_utils.to_upper_camel_case('pythonic_case'),
            'PythonicCase'
        )
        self.assertEqual(
            waferslim.import_utils.to_upper_camel_case('CamelCase'),
            'CamelCase'
        )
        self.assertEqual(
            waferslim.import_utils.to_upper_camel_case('camelCase'),
            'CamelCase'
        )

    def test_pythonic_case(self):
        self.assertEqual(
            waferslim.import_utils.to_pythonic('pythonicCase'),
            'pythonic_case'
        )
        self.assertEqual(
            waferslim.import_utils.to_pythonic('CamelCase'),
            'camel_case'
        )
        self.assertEqual(
            waferslim.import_utils.to_pythonic('camelCase'),
            'camel_case'
        )

    def test_aliases(self):
        result = waferslim.import_utils.get_aliases(['pythonic_case', 'CamelCase'])
        self.assertEqual(result,
            {
                'pythonic_case': 'pythonic_case',
                'pythonicCase': 'pythonic_case',
                'PythonicCase': 'pythonic_case',
                'CamelCase': 'CamelCase',
                'camelCase': 'CamelCase',
            }
        )


class GetClassesTestCase(unittest.TestCase):
    def test_get_classes_finds_only_methods(self):
        classes = list(waferslim.import_utils.get_classes(echo_fixture))
        self.assertEqual(len(classes), 1)
        name, data = classes[0]
        self.assertEqual(name, 'EchoFixture')
        self.assertEqual(
            set(['class_echo', 'static_echo', 'echo']),
            set(data['methods'])
        )


if __name__ == '__main__':
    unittest.main()
