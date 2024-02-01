#
# Project:   vim-mail-refs
# Copyright: (c) 2016 by Daniela Ďuričeková <daniela.duricekova@protonmail.com>
#            and contributors
# License:   MIT, see the LICENSE file for more details
#

import unittest

from vim_mail_refs import Ref
from vim_mail_refs import RefWithUrl
from vim_mail_refs import add_ref
from vim_mail_refs import fix_mail_refs
from vim_mail_refs import get_refs_with_urls_for_menu


class RefTests(unittest.TestCase):
    def test_number_is_accessible_after_creation(self):
        ref = Ref(5)

        self.assertEqual(ref.number, 5)

    def test_number_has_to_be_positive(self):
        with self.assertRaises(ValueError):
            Ref(0)

    def test_str_returns_correct_string(self):
        ref = Ref(5)

        self.assertEqual(str(ref), "[5]")

    def test_from_str_returns_correct_ref(self):
        ref = Ref.from_str('[1]')

        self.assertEqual(ref.number, 1)

    def test_from_str_return_None_when_str_cannot_be_parsed(self):
        self.assertIsNone(Ref.from_str(''))

    def test_refs_are_compared_by_their_numbers(self):
        self.assertEqual(Ref(1), Ref(1))
        self.assertNotEqual(Ref(1), Ref(2))
        self.assertLess(Ref(1), Ref(2))
        self.assertGreater(Ref(2), Ref(1))
        self.assertLessEqual(Ref(1), Ref(1))
        self.assertGreaterEqual(Ref(2), Ref(1))

    def test_can_be_put_into_set(self):
        {Ref(1)}


class RefWithUrlTests(unittest.TestCase):
    def test_attributes_are_accessible_after_creation(self):
        ref_with_url = RefWithUrl(Ref(1), 'URL')

        self.assertEqual(ref_with_url.ref, Ref(1))
        self.assertEqual(ref_with_url.url, 'URL')

    def test_str_returns_correct_string(self):
        ref_with_url = RefWithUrl(Ref(1), 'URL')

        self.assertEqual(str(ref_with_url), '[1] URL')

    def test_from_str_returns_correct_ref_with_url(self):
        ref_with_url = RefWithUrl.from_str('[1] URL')

        self.assertEqual(ref_with_url.ref, Ref(1))
        self.assertEqual(ref_with_url.url, 'URL')

    def test_from_str_returns_None_when_str_cannot_be_parsed(self):
        self.assertIsNone(RefWithUrl.from_str(''))


class AddRefTests(unittest.TestCase):
    def test_ref_is_added_correctly_when_buffer_is_empty(self):
        buffer = ['']

        new_cursor = add_ref(buffer, cursor=(0, 0), ref_or_url='URL')

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

        new_cursor = add_ref(buffer, cursor=(0, 7), ref_or_url='URL')

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

        new_cursor = add_ref(buffer, cursor=(0, 7), ref_or_url='URL')

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

        new_cursor = add_ref(buffer, cursor=(1, 12), ref_or_url='URL2')

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

        new_cursor = add_ref(buffer, cursor=(0, 11), ref_or_url='URL2')

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

        new_cursor = add_ref(buffer, cursor=(0, 6), ref_or_url='URL')

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

        new_cursor = add_ref(buffer, cursor=(0, 5), ref_or_url='URL')

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

        new_cursor = add_ref(buffer, cursor=(0, 7), ref_or_url='URL')

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

    def test_ref_is_added_correctly_when_word_contains_special_chars(self):
        buffer = ['look at 3f5-4_2.']
        #                    ^

        new_cursor = add_ref(buffer, cursor=(0, 10), ref_or_url='URL')

        self.assertEqual(
            buffer,
            [
                'look at 3f5-4_2 [1].',
                #                ^
                '',
                '[1] URL'
            ]
        )
        self.assertEqual(new_cursor, (0, 18))

    def test_does_not_add_redundant_space(self):
        buffer = ['look at .']
        #                  ^

        new_cursor = add_ref(buffer, cursor=(0, 8), ref_or_url='URL')

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

        new_cursor = add_ref(buffer, cursor=(1, 12), ref_or_url='URL1')

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

        new_cursor = add_ref(buffer, cursor=(0, 7), ref_or_url='URL')

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

        new_cursor = add_ref(buffer, cursor=(0, 7), ref_or_url='URL')

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

        new_cursor = add_ref(buffer, cursor=(0, 7), ref_or_url='URL')

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

    def test_adds_reference_when_ref_or_url_is_reference(self):
        buffer = [
            'look at [1].',
            'Also look at .',
            #            ^
            '',
            '[1] URL1'
        ]

        new_cursor = add_ref(buffer, cursor=(1, 12), ref_or_url='[1]')

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

    def test_adds_reference_when_ref_or_url_is_reference_number(self):
        buffer = [
            'look at [1].',
            'Also look at .',
            #            ^
            '',
            '[1] URL1'
        ]

        new_cursor = add_ref(buffer, cursor=(1, 12), ref_or_url='1')

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


class GetRefsWithUrlsForMenuTests(unittest.TestCase):
    def test_return_empty_list_when_there_are_no_references(self):
        buffer = []

        refs_with_urls = get_refs_with_urls_for_menu(buffer)

        self.assertEqual(refs_with_urls, [])

    def test_returns_correct_list_when_there_are_references(self):
        buffer = [
            'look at [1].',
            'also look at [2].',
            '',
            '[1] url1',
            '[2] url2'
        ]

        refs_with_urls = get_refs_with_urls_for_menu(buffer)

        self.assertEqual(
            refs_with_urls,
            [
                '[1] url1',
                '[2] url2'
            ]
        )

    def test_returns_correct_list_when_there_is_signature(self):
        buffer = [
            'look at [1].',
            '',
            '[1] url1',
            '',
            '-- ',
            'Signature',
            '[5] xxx'
        ]

        refs_with_urls = get_refs_with_urls_for_menu(buffer)

        self.assertEqual(
            refs_with_urls,
            [
                '[1] url1'
            ]
        )


class FixMailRefsTests(unittest.TestCase):
    def test_adds_empty_line_before_signature_where_there_is_none(self):
        buffer = [
            'Hello!',
            '-- ',
            'Signature'
            #    ^
        ]

        new_cursor = fix_mail_refs(buffer, cursor=(2, 4))

        self.assertEqual(
            buffer,
            [
                'Hello!',
                '',
                '-- ',
                #^
                'Signature'
            ]
        )
        self.assertEqual(new_cursor, (2, 0))

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

        new_cursor = fix_mail_refs(buffer, cursor=(1, 15))

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

        new_cursor = fix_mail_refs(buffer, cursor=(1, 15))

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

        new_cursor = fix_mail_refs(buffer, cursor=(0, 5))

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

        new_cursor = fix_mail_refs(buffer, cursor=(0, 2))

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

        new_cursor = fix_mail_refs(buffer, cursor=(0, 5))

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

        new_cursor = fix_mail_refs(buffer, cursor=(2, 7))

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

        new_cursor = fix_mail_refs(buffer, cursor=(1, 4))

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

        new_cursor = fix_mail_refs(buffer, cursor=(3, 4))

        self.assertEqual(buffer, orig_buffer)
        self.assertEqual(new_cursor, (3, 4))

    def test_refs_are_not_renumbered_when_do_not_need_to_be_renumbered(self):
        buffer = [
            'look at [1].',
            'Also look at [2].',
            #               ^
            '',
            '[1] URL1',
            '[2] URL2'
        ]
        orig_buffer = buffer[:]

        new_cursor = fix_mail_refs(buffer, cursor=(1, 15))

        self.assertEqual(buffer, orig_buffer)
        self.assertEqual(new_cursor, (1, 15))

    def test_refs_are_renumbered_when_two_refs_need_to_be_switched(self):
        buffer = [
            'look at [2].',
            'Also look at [1].',
            #               ^
            '',
            '[1] URL2',
            '[2] URL1'
        ]

        new_cursor = fix_mail_refs(buffer, cursor=(1, 15))

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

    def test_refs_are_renumbered_correctly_when_ref_size_decreases(self):
        buffer = [
            'look at [10].',
            #            ^
            '',
            '[10] URL1'
        ]

        new_cursor = fix_mail_refs(buffer, cursor=(0, 12))

        self.assertEqual(
            buffer,
            [
                'look at [1].',
                #^
                '',
                '[1] URL1'
            ]
        )
        self.assertEqual(new_cursor, (0, 0))

    def test_refs_are_renumbered_correctly_when_ref_size_increases(self):
        buffer = [
            'look at [10], [9], [8], [7], [6], [5], [4], [3], [2], [1].',
            #            ^
            '',
            '[10] URL1',
            '[9] URL2',
            '[8] URL3',
            '[7] URL4',
            '[6] URL5',
            '[5] URL6',
            '[4] URL7',
            '[3] URL8',
            '[2] URL9',
            '[1] URL10'
        ]

        new_cursor = fix_mail_refs(buffer, cursor=(0, 12))

        self.assertEqual(
            buffer,
            [
                'look at [1], [2], [3], [4], [5], [6], [7], [8], [9], [10].',
                #            ^
                '',
                '[1] URL1',
                '[2] URL2',
                '[3] URL3',
                '[4] URL4',
                '[5] URL5',
                '[6] URL6',
                '[7] URL7',
                '[8] URL8',
                '[9] URL9',
                '[10] URL10'
            ]
        )
        self.assertEqual(new_cursor, (0, 12))
