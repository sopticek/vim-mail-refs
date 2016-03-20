import unittest
from unittest import mock

from vim_mail_refs import add_ref
from vim_mail_refs import norm_mail_refs


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

    def test_trailing_empty_lines_are_removed(self):
        buffer = [
            '[1]. Look at',
            #           ^
            '',
            '[1] URL1',
            '',
        ]

        self.window.cursor = (1, 11)
        ref_url = 'URL2'

        add_ref(buffer, self.window, ref_url)

        self.assertEqual(
            buffer,
            [
                '[1]. Look at [2]',
                #               ^
                '',
                '[1] URL1',
                '[2] URL2',
            ]
        )
        self.assertEqual(self.window.cursor, (1, 15))

    def test_space_is_added_before_ref_when_cursor_is_on_word_end(self):
        buffer = ['look at.']
        #                ^
        self.window.cursor = (1, 6)
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

    def test_ref_is_added_correctly_when_cursor_is_inside_word(self):
        buffer = ['look at.']
        #               ^
        self.window.cursor = (1, 5)
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

    def test_ref_is_added_correctly_when_cursor_is_at_period(self):
        buffer = ['look at.']
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

    def test_does_not_add_redundant_space(self):
        buffer = ['look at .']
        #                  ^
        self.window.cursor = (1, 8)
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

    def test_uses_existing_ref_when_url_has_already_been_added(self):
        buffer = [
            'look at [1].',
            'Also look at .',
            #            ^
            '',
            '[1] URL1'
        ]
        self.window.cursor = (2, 12)
        ref_url = 'URL1'

        add_ref(buffer, self.window, ref_url)

        self.assertEqual(
            buffer,
            [
                'look at [1].',
                'Also look at [1].',
                #               ^
                '',
                '[1] URL1'
            ]
        )
        self.assertEqual(self.window.cursor, (2, 15))

    def test_does_not_add_redundant_empty_lines_before_reference_list(self):
        buffer = [
            'look at ',
            #       ^
            ''
        ]
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

    def test_reference_list_is_placed_before_signature(self):
        buffer = [
            'look at ',
            #       ^
            '--',
            'Signature'
        ]
        self.window.cursor = (1, 7)
        ref_url = 'URL'

        add_ref(buffer, self.window, ref_url)

        self.assertEqual(
            buffer,
            [
                'look at [1]',
                #          ^
                '',
                '[1] URL',
                '',
                '--',
                'Signature'
            ]
        )
        self.assertEqual(self.window.cursor, (1, 10))

    def test_does_not_add_redundant_empty_line_before_signature(self):
        buffer = [
            'look at ',
            #       ^
            '',
            '--',
            'Signature'
        ]
        self.window.cursor = (1, 7)
        ref_url = 'URL'

        add_ref(buffer, self.window, ref_url)

        self.assertEqual(
            buffer,
            [
                'look at [1]',
                #          ^
                '',
                '[1] URL',
                '',
                '--',
                'Signature'
            ]
        )
        self.assertEqual(self.window.cursor, (1, 10))


class NormMailRefsTests(unittest.TestCase):
    def setUp(self):
        self.window = mock.Mock()

    def test_does_nothing_when_there_is_nothing_to_be_done(self):
        buffer = [
            'look at [1].',
            'Also look at [2].',
            #               ^
            '',
            '[1] URL1',
            '[2] URL2',
            '',
            '-- ',
            'Signature'
        ]
        self.window.cursor = (2, 15)
        orig_buffer = buffer[:]

        norm_mail_refs(buffer, self.window)

        self.assertEqual(buffer, orig_buffer)
        self.assertEqual(self.window.cursor, (2, 15))

    def test_unused_references_are_removed(self):
        buffer = [
            'look at [1].',
            'Also look at the sky.',
            #               ^
            '',
            '[1] URL1',
            '[2] URL2',
            '[3] URL3',
            '',
            '-- ',
            'Signature'
        ]
        self.window.cursor = (2, 15)

        norm_mail_refs(buffer, self.window)

        self.assertEqual(
            buffer,
            [
                'look at [1].',
                'Also look at the sky.',
                #               ^
                '',
                '[1] URL1',
                '',
                '-- ',
                'Signature'
            ]
        )
        self.assertEqual(self.window.cursor, (2, 15))

    def test_empty_lines_are_squashed_into_one(self):
        buffer = [
            'Hello!',
            #     ^
            '',
            '[1] URL1',
            '[2] URL2',
            '[3] URL3',
            '',
            '-- ',
            'Signature'
        ]
        self.window.cursor = (1, 5)

        norm_mail_refs(buffer, self.window)

        self.assertEqual(
            buffer,
            [
                'Hello!',
                #     ^
                '',
                '-- ',
                'Signature'
            ]
        )
        self.assertEqual(self.window.cursor, (1, 5))
