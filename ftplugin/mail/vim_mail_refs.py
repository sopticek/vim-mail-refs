#
# Author:   Daniela Duricekova <daniela.duricekova@gmail.com>
# Date:     2016-03-18
#

import re


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


def add_ref(buffer, cursor, ref_url):
    '''Adds a reference to ref_url into the buffer, including adding ref_url to
    the end of the buffer.
    '''
    row, col = cursor
    signature = _remove_signature(buffer)
    _remove_trailing_empty_lines(buffer)
    ref = _append_ref_url(buffer, ref_url)
    row, col = _insert_ref(buffer, row, col, ref)
    _add_signature(buffer, signature)
    return row, col


def fix_mail_refs(buffer, cursor):
    '''Normalizes all references used in the buffer.

    The following normalizations are performed:
    - unused references are removed
    '''
    signature = _remove_signature(buffer)
    _remove_trailing_empty_lines(buffer)
    _remove_unused_refs_with_urls(buffer)
    _remove_trailing_empty_lines(buffer)
    _add_signature(buffer, signature)
    row, col = _put_cursor_at_valid_pos(buffer, cursor)
    return row, col


def _append_ref_url(buffer, ref_url):
    '''Appends ref_url to the list of references at the end of the buffer.
    '''
    refs = _get_refs_with_urls(buffer)
    _add_empty_line_before_ref_list_if_needed(buffer, refs)

    ref, ref_exists = _get_ref_for_url(refs, ref_url)
    if not ref_exists:
        buffer.append('{} {}'.format(ref, ref_url))
    return ref


def _insert_ref(buffer, row, col, ref):
    '''Inserts the reference into the current line in the buffer.
    '''
    line = buffer[row]

    if not line:
        buffer[row] = ref
        return row, col + len(ref) - 1

    line, col = _prepare_line_for_ref_insert(line, col)
    buffer[row] = '{} {}{}'.format(
        line[:col],
        ref,
        line[col:]
    )
    return row, col + len(ref)


def _prepare_line_for_ref_insert(line, col):
    '''Returns (line, col) so that the caller can safely insert ' [x]' at
    line[col], without introducing redundant spaces.
    '''
    # Get to the first non-alpha character.
    while col < len(line) and line[col].isalpha():
        col += 1

    # Get to the leftmost space.
    while col > 0 and line[col - 1].isspace():
        col -= 1

    # Remove all spaces.
    while col < len(line) and line[col].isspace():
        line = line[:col] + line[col + 1:]

    return line, col


def _get_refs_with_urls(buffer):
    '''Returns all references with URLs from the buffer.
    '''
    refs = []
    for line in reversed(buffer):
        m = re.match(r'(\[\d+\]) (.+)', line)
        if m is None:
            break
        refs.append(m.groups())
    return list(reversed(refs))


def _get_ref_for_url(refs, ref_url):
    '''Returns (ref, ref_exists) for ref_url based on existing refs.
    '''
    for ref, url in refs:
        if url == ref_url:
            return ref, True
    return '[{}]'.format(len(refs) + 1), False


def _add_empty_line_before_ref_list_if_needed(buffer, refs):
    if not refs:
        buffer.append('')


def _remove_signature(buffer):
    for i, line in enumerate(reversed(buffer)):
        if re.match(SIGNATURE_START_RE, line):
            break
    else:  # No break.
        return []

    sig_slice = slice(-(i + 1), len(buffer))
    signature = buffer[sig_slice]
    del buffer[sig_slice]
    return signature


def _add_signature(buffer, signature):
    _add_block(buffer, signature)


def _remove_trailing_empty_lines(buffer):
    if len(buffer) <= 1 or buffer[-1]:
        return

    for i, line in enumerate(reversed(buffer)):
        if line:
            break

    del buffer[-i:]


def _remove_unused_refs_with_urls(buffer):
    refs_with_urls = _remove_refs_with_urls(buffer)
    used_refs = _get_used_refs(buffer)
    new_refs_with_urls = [
        (ref, url) for ref, url in refs_with_urls if ref in used_refs
    ]
    _add_refs_with_urls(buffer, new_refs_with_urls)


def _remove_refs_with_urls(buffer):
    refs = _get_refs_with_urls(buffer)
    if refs:
        del buffer[-len(refs):]
    return refs


def _add_refs_with_urls(buffer, refs_with_urls):
    lines = [' '.join(ref_with_url) for ref_with_url in refs_with_urls]
    _add_block(buffer, lines)


def _get_used_refs(buffer):
    used_refs = set()
    for line in buffer:
        used_refs |= _get_used_refs_in_line(line)
    return used_refs


def _get_used_refs_in_line(line):
    return set(re.findall(REF_RE, line))


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
    if row < len(buffer) and col < len(buffer[row]):
        return row, col

    # We have to put the cursor at a valid position.
    row = len(buffer) - 1
    if col >= len(buffer[row]):
        col = 0

    return row, col
