#
# Author:   Daniela Duricekova <daniela.duricekova@gmail.com>
# Date:     2016-03-18
#

import re

from collections import namedtuple
from contextlib import contextmanager
from functools import total_ordering


# Regular expression matching the start of a mail signature.
SIGNATURE_START_RE = r'^--\s*$'

# Regular expression matching reference in text.
REF_RE = re.compile(
    r'''
    (?<!\w|\]|\)) # What cannot be before reference.
    (\[\d+\])     # Format of reference.
    (?!\[)        # What cannot be after reference.
    ''', re.VERBOSE
)

# Regular expression matching a word.
WORD_RE = r'[-\w_]+'


@total_ordering
class Ref:
    def __init__(self, number):
        if number < 1:
            raise ValueError('number has to be positive')
        self._number = number

    @property
    def number(self):
        return self._number

    @classmethod
    def from_str(cls, s):
        m = re.match(r'\[(\d+)\]', s)
        if m is None:
            return None
        return cls(int(m.group(1)))

    def __str__(self):
        return '[{}]'.format(self.number)

    def __eq__(self, other):
        return self.number == other.number

    def __lt__(self, other):
        return self.number < other.number

    def __hash__(self):
        return hash(self.number)


class RefWithUrl(namedtuple('RefWithUrl', ['ref', 'url'])):
    def __str__(self):
        return '{} {}'.format(self.ref, self.url)

    @classmethod
    def from_str(cls, s):
        m = re.match(r'\[(\d+)\] (.+)', s)
        if m is None:
            return None
        return cls(ref=Ref(int(m.group(1))), url=m.group(2))


def add_ref(buffer, cursor, ref_url):
    '''Adds a reference to ref_url into the buffer, including adding ref_url to
    the end of the buffer.
    '''
    row, col = cursor
    with _removed_signature(buffer):
        _remove_trailing_empty_lines(buffer)
        ref = _append_ref_url(buffer, ref_url)
        row, col = _insert_ref(buffer, row, col, ref)
    return row, col


def fix_mail_refs(buffer, cursor):
    '''Normalizes all references used in the buffer.

    The following normalizations are performed:
    - unused references are removed
    - references are renumbered by their position in the buffer ([1], [2], ...)
    '''
    with _removed_signature(buffer):
        _remove_trailing_empty_lines(buffer)
        _remove_unused_refs_with_urls(buffer)
        _remove_trailing_empty_lines(buffer)
        _renumber_refs(buffer)
    row, col = _put_cursor_at_valid_pos(buffer, cursor)
    return row, col


@contextmanager
def _removed_signature(buffer):
    for i, line in enumerate(reversed(buffer)):
        if re.match(SIGNATURE_START_RE, line):
            sig_slice = slice(-(i + 1), len(buffer))
            signature = buffer[sig_slice]
            del buffer[sig_slice]
            break
    else:  # No break.
        signature = []

    try:
        yield signature
    finally:
        _add_block(buffer, signature)


def _append_ref_url(buffer, ref_url):
    '''Appends ref_url to the list of references at the end of the buffer.
    '''
    refs = _get_refs_with_urls(buffer)
    _add_empty_line_before_ref_list_if_needed(buffer, refs)

    ref, ref_exists = _get_ref_for_url(refs, ref_url)
    if not ref_exists:
        ref_with_url = RefWithUrl(ref, ref_url)
        buffer.append(str(ref_with_url))
    return ref


def _insert_ref(buffer, row, col, ref):
    '''Inserts the reference into the current line in the buffer.
    '''
    line = buffer[row]

    if not line:
        buffer[row] = str(ref)
        return row, len(buffer[row]) - 1

    line, col = _prepare_line_for_ref_insert(line, col)
    buffer[row] = '{} {}{}'.format(
        line[:col],
        ref,
        line[col:]
    )
    return row, col + len(str(ref))


def _prepare_line_for_ref_insert(line, col):
    '''Returns (line, col) so that the caller can safely insert ' [x]' at
    line[col], without introducing redundant spaces.
    '''
    # Get to the first non-word character.
    while col < len(line) and _is_part_of_word(line[col]):
        col += 1

    # Get to the leftmost space.
    while col > 0 and line[col - 1].isspace():
        col -= 1

    # Remove all spaces.
    while col < len(line) and line[col].isspace():
        line = line[:col] + line[col + 1:]

    return line, col


def _is_part_of_word(s):
    return re.fullmatch(WORD_RE, s) is not None


def _get_refs_with_urls(buffer):
    '''Returns all references with URLs from the buffer.
    '''
    refs = []
    for line in reversed(buffer):
        ref_with_url = RefWithUrl.from_str(line)
        if ref_with_url is not None:
            refs.append(ref_with_url)
    return list(reversed(refs))


def _get_ref_for_url(refs, ref_url):
    '''Returns (ref, ref_exists) for ref_url based on existing refs.
    '''
    for ref, url in refs:
        if url == ref_url:
            return ref, True
    return Ref(len(refs) + 1), False


def _add_empty_line_before_ref_list_if_needed(buffer, refs):
    if not refs:
        buffer.append('')


def _remove_trailing_empty_lines(buffer):
    if len(buffer) <= 1 or buffer[-1]:
        return

    for i, line in enumerate(reversed(buffer)):
        if line:
            break

    del buffer[-i:]


def _renumber_refs(buffer):
    with _removed_refs_with_urls(buffer) as refs_with_urls:
        ref_map = _renumber_refs_in_mail_body(buffer)
        _update_refs_with_urls(refs_with_urls, ref_map)


def _renumber_refs_in_mail_body(buffer):
    ref_counter = 1
    ref_map = {}
    row, col = 0, 0

    while True:
        pos = _get_next_ref_pos(buffer, row, col)
        if pos is None:
            break
        row, (col_start, col_end) = pos
        ref = Ref.from_str(buffer[row][col_start:col_end])
        new_ref = ref_map.setdefault(ref, Ref(ref_counter))
        if new_ref.number == ref_counter:
            ref_counter += 1
        row, col = _replace_ref(buffer, row, col_start, col_end, new_ref)

    return ref_map


def _get_next_ref_pos(buffer, row, col):
    for r in range(row, len(buffer)):
        for m in re.finditer(REF_RE, buffer[r][col:]):
            return r, (col + m.start(1), col + m.end(1))
        col = 0


def _replace_ref(buffer, row, col_start, col_end, new_ref):
    line = buffer[row][:col_start] + str(new_ref) + buffer[row][col_end:]
    buffer[row] = line
    return row, col_start + len(str(new_ref))


def _update_refs_with_urls(refs_with_urls, ref_map):
    for i, (ref, url) in enumerate(refs_with_urls):
        refs_with_urls[i] = RefWithUrl(ref_map[ref], url)
    refs_with_urls.sort()


@contextmanager
def _removed_refs_with_urls(buffer):
    refs_with_urls = _remove_refs_with_urls(buffer)
    try:
        yield refs_with_urls
    finally:
        _add_refs_with_urls(buffer, refs_with_urls)


def _remove_unused_refs_with_urls(buffer):
    with _removed_refs_with_urls(buffer) as refs_with_urls:
        used_refs = _get_used_refs(buffer)
        new_refs_with_urls = [
            RefWithUrl(ref, url)
            for ref, url in refs_with_urls
            if ref in used_refs
        ]
        refs_with_urls[:] = new_refs_with_urls


def _remove_refs_with_urls(buffer):
    refs = _get_refs_with_urls(buffer)
    if refs:
        del buffer[-len(refs):]
    return refs


def _add_refs_with_urls(buffer, refs_with_urls):
    lines = [str(ref_with_url) for ref_with_url in refs_with_urls]
    _add_block(buffer, lines)


def _get_used_refs(buffer):
    used_refs = set()
    for line in buffer:
        used_refs |= _get_used_refs_in_line(line)
    return used_refs


def _get_used_refs_in_line(line):
    return set(Ref.from_str(s) for s in re.findall(REF_RE, line))


def _add_block(buffer, lines):
    if not lines:
        return

    if buffer[-1]:
        buffer.append('')

    # We cannot use buffer.extend() because Vim buffers do not support it.
    for line in lines:
        buffer.append(line)


def _put_cursor_at_valid_pos(buffer, cursor):
    row, col = cursor
    if row >= len(buffer):
        row = len(buffer) - 1
    if col >= len(buffer[row]):
        col = 0
    return row, col
