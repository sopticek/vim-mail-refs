import unittest

from vim_mail_refs import add_ref
from vim_mail_refs import norm_mail_refs


class AddRefTests(unittest.TestCase):
    def test_ref_is_added_correctly_when_buffer_is_empty(self):
        buffer = ['']

        new_cursor = add_ref(buffer, cursor=(0, 0), ref_url='URL')

        self.assertEqual(
            buffer,
            [
                '[1]',
                #  ^
                '',
                '[1] URL'
            ]
        )
        self.assertEqual(new_cursor, (0, 2))

    def test_ref_is_appended_correctly_when_buffer_is_not_empty(self):
        buffer = ['look at ']
        #                 ^

        new_cursor = add_ref(buffer, cursor=(0, 7), ref_url='URL')

        self.assertEqual(
            buffer,
            [
                'look at [1]',
                #          ^
                '',
                '[1] URL'
            ]
        )
        self.assertEqual(new_cursor, (0, 10))

    def test_ref_is_inserted_correctly_when_buffer_is_not_empty(self):
        buffer = ['look at .']
        #                 ^

        new_cursor = add_ref(buffer, cursor=(0, 7), ref_url='URL')

        self.assertEqual(
            buffer,
            [
                'look at [1].',
                #          ^
                '',
                '[1] URL'
            ]
        )
        self.assertEqual(new_cursor, (0, 10))

    def test_second_ref_is_added_correctly(self):
        buffer = [
            'look at [1].',
            'Also look at .',
            #            ^
            '',
            '[1] URL1'
        ]

        new_cursor = add_ref(buffer, cursor=(1, 12), ref_url='URL2')

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
        self.assertEqual(new_cursor, (1, 15))

    def test_trailing_empty_lines_are_removed(self):
        buffer = [
            '[1]. Look at',
            #           ^
            '',
            '[1] URL1',
            '',
        ]

        new_cursor = add_ref(buffer, cursor=(0, 11), ref_url='URL2')

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
        self.assertEqual(new_cursor, (0, 15))

    def test_space_is_added_before_ref_when_cursor_is_on_word_end(self):
        buffer = ['look at.']
        #                ^

        new_cursor = add_ref(buffer, cursor=(0, 6), ref_url='URL')

        self.assertEqual(
            buffer,
            [
                'look at [1].',
                #          ^
                '',
                '[1] URL'
            ]
        )
        self.assertEqual(new_cursor, (0, 10))

    def test_ref_is_added_correctly_when_cursor_is_inside_word(self):
        buffer = ['look at.']
        #               ^

        new_cursor = add_ref(buffer, cursor=(0, 5), ref_url='URL')

        self.assertEqual(
            buffer,
            [
                'look at [1].',
                #          ^
                '',
                '[1] URL'
            ]
        )
        self.assertEqual(new_cursor, (0, 10))

    def test_ref_is_added_correctly_when_cursor_is_at_period(self):
        buffer = ['look at.']
        #                 ^

        new_cursor = add_ref(buffer, cursor=(0, 7), ref_url='URL')

        self.assertEqual(
            buffer,
            [
                'look at [1].',
                #          ^
                '',
                '[1] URL'
            ]
        )
        self.assertEqual(new_cursor, (0, 10))

    def test_does_not_add_redundant_space(self):
        buffer = ['look at .']
        #                  ^

        new_cursor = add_ref(buffer, cursor=(0, 8), ref_url='URL')

        self.assertEqual(
            buffer,
            [
                'look at [1].',
                #          ^
                '',
                '[1] URL'
            ]
        )
        self.assertEqual(new_cursor, (0, 10))

    def test_uses_existing_ref_when_url_has_already_been_added(self):
        buffer = [
            'look at [1].',
            'Also look at .',
            #            ^
            '',
            '[1] URL1'
        ]

        new_cursor = add_ref(buffer, cursor=(1, 12), ref_url='URL1')

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
        self.assertEqual(new_cursor, (1, 15))

    def test_does_not_add_redundant_empty_lines_before_reference_list(self):
        buffer = [
            'look at ',
            #       ^
            ''
        ]

        new_cursor = add_ref(buffer, cursor=(0, 7), ref_url='URL')

        self.assertEqual(
            buffer,
            [
                'look at [1]',
                #          ^
                '',
                '[1] URL'
            ]
        )
        self.assertEqual(new_cursor, (0, 10))

    def test_reference_list_is_placed_before_signature(self):
        buffer = [
            'look at ',
            #       ^
            '--',
            'Signature'
        ]

        new_cursor = add_ref(buffer, cursor=(0, 7), ref_url='URL')

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
        self.assertEqual(new_cursor, (0, 10))

    def test_does_not_add_redundant_empty_line_before_signature(self):
        buffer = [
            'look at ',
            #       ^
            '',
            '--',
            'Signature'
        ]

        new_cursor = add_ref(buffer, cursor=(0, 7), ref_url='URL')

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
        self.assertEqual(new_cursor, (0, 10))


class NormMailRefsTests(unittest.TestCase):
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
        orig_buffer = buffer[:]

        new_cursor = norm_mail_refs(buffer, cursor=(1, 15))

        self.assertEqual(buffer, orig_buffer)
        self.assertEqual(new_cursor, (1, 15))

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

        new_cursor = norm_mail_refs(buffer, cursor=(1, 15))

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
        self.assertEqual(new_cursor, (1, 15))

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

        new_cursor = norm_mail_refs(buffer, cursor=(0, 5))

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
        self.assertEqual(new_cursor, (0, 5))

    def test_keeps_standalone_reference_on_line(self):
        buffer = [
            '[1]',
            #  ^
            '',
            '[1] URL1'
        ]
        orig_buffer = buffer[:]

        new_cursor = norm_mail_refs(buffer, cursor=(0, 2))

        self.assertEqual(buffer, orig_buffer)
        self.assertEqual(new_cursor, (0, 2))

    def test_does_not_consider_subscripts_in_code_as_references(self):
        buffer = [
            'Hello!',
            #     ^
            '[1][0]',
            'x[2] = 2',
            'x1[3] = 3',
            'x_[4] = 4',
            'range(10)[5]',
            'x = [0, 1, 2, 3, 4, 5, 6][6]',
            '[0, 1, 2, 3, 4, 5, 6, 7][7]',
            '',
            '[1] URL1',
            '[2] URL2',
            '[3] URL3',
            '[4] URL4',
            '[5] URL5',
            '[6] URL6',
            '[7] URL7'
        ]

        new_cursor = norm_mail_refs(buffer, cursor=(0, 5))

        self.assertEqual(
            buffer,
            [
                'Hello!',
                #     ^
                '[1][0]',
                'x[2] = 2',
                'x1[3] = 3',
                'x_[4] = 4',
                'range(10)[5]',
                'x = [0, 1, 2, 3, 4, 5, 6][6]',
                '[0, 1, 2, 3, 4, 5, 6, 7][7]'
            ]
        )
        self.assertEqual(new_cursor, (0, 5))

    def test_cursor_is_at_start_of_prev_line_when_col_no_longer_exists(self):
        buffer = [
            'Hi!',
            'Hello!',
            '[1] URL1'
            #       ^
        ]

        new_cursor = norm_mail_refs(buffer, cursor=(2, 7))

        self.assertEqual(
            buffer,
            [
                'Hi!',
                'Hello!'
                #^
            ]
        )
        self.assertEqual(new_cursor, (1, 0))

    def test_cursor_is_at_prev_line_at_same_col_when_col_exists(self):
        buffer = [
            'Hello!',
            '[1] URL1'
            #    ^
        ]

        new_cursor = norm_mail_refs(buffer, cursor=(1, 4))

        self.assertEqual(
            buffer,
            [
                'Hello!'
                #    ^
            ]
        )
        self.assertEqual(new_cursor, (0, 4))

    def test_cursor_stays_on_signature_when_nothing_is_removed(self):
        buffer = [
            'Hello!',
            '',
            '-- ',
            'Signature'
            #    ^
        ]
        orig_buffer = buffer[:]

        new_cursor = norm_mail_refs(buffer, cursor=(3, 4))

        self.assertEqual(buffer, orig_buffer)
        self.assertEqual(new_cursor, (3, 4))
