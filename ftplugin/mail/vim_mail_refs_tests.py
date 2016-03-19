import unittest
from unittest import mock

from vim_mail_refs import add_ref


class AddRefTests(unittest.TestCase):
    def setUp(self):
        self.window = mock.Mock()

    def test_ref_is_added_correctly_when_buffer_is_empty(self):
        buffer = ['']
        self.window.cursor = (1, 0)
        ref_url = 'URL'

        add_ref(buffer, self.window, ref_url)

        self.assertEqual(
            buffer,
            [
                '[1]',
                #  ^
                '',
                '[1] URL'
            ]
        )
        self.assertEqual(self.window.cursor, (1, 2))

    def test_ref_is_appended_correctly_when_buffer_is_not_empty(self):
        buffer = ['look at ']
        #                 ^
        self.window.cursor = (1, 7)
        ref_url = 'URL'

        add_ref(buffer, self.window, ref_url)

        self.assertEqual(
            buffer,
            [
                'look at [1]',
                #          ^
                '',
                '[1] URL'
            ]
        )
        self.assertEqual(self.window.cursor, (1, 10))

    def test_ref_is_inserted_correctly_when_buffer_is_not_empty(self):
        buffer = ['look at .']
        #                 ^
        self.window.cursor = (1, 7)
        ref_url = 'URL'

        add_ref(buffer, self.window, ref_url)

        self.assertEqual(
            buffer,
            [
                'look at [1].',
                #          ^
                '',
                '[1] URL'
            ]
        )
        self.assertEqual(self.window.cursor, (1, 10))

    def test_second_ref_is_added_correctly(self):
        buffer = [
            'look at [1].',
            'Also look at .',
            #            ^
            '',
            '[1] URL1'
        ]
        self.window.cursor = (2, 12)
        ref_url = 'URL2'

        add_ref(buffer, self.window, ref_url)

        self.assertEqual(
            buffer,
            [
                'look at [1].',
                'Also look at [2].',
                #               ^
                '',
                '[1] URL1',
                '[2] URL2'
            ]
        )
        self.assertEqual(self.window.cursor, (2, 15))
