#
# Author:   Daniela Duricekova <daniela.duricekova@gmail.com>
# Date:     2016-03-18
#

import re


# Regular expression matching the start of a mail signature.
SIGNATURE_START_RE = r'^--\s*$'


def add_ref(buffer, window, ref_url):
    '''Adds a reference to ref_url into the buffer, including adding ref_url to
    the end of the buffer.
    '''
    row, col = _get_cursor_pos(window)
    signature = _remove_signature(buffer)
    ref = _append_ref_url(buffer, ref_url)
    row, col = _insert_ref(buffer, row, col, ref)
    _add_signature(buffer, signature)
    _set_cursor_pos(window, row, col)


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
    return refs


def _get_ref_for_url(refs, ref_url):
    '''Returns (ref, ref_exists) for ref_url based on existing refs.
    '''
    for ref, url in refs:
        if url == ref_url:
            return ref, True
    return '[{}]'.format(len(refs) + 1), False


def _get_cursor_pos(window):
    row, col = window.cursor
    return row - 1, col


def _set_cursor_pos(window, row, col):
    window.cursor = (row + 1, col)


def _add_empty_line_before_ref_list_if_needed(buffer, refs):
    # When there already are references, the empty line has already been added.
    if refs:
        return

    # When there already is an empty line, do not add another one.
    if len(buffer) >= 2 and buffer[-1] == '':
        return

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
    if not signature:
        return

    if buffer[-1] != '':
        buffer.append('')

    # We cannot use buffer.extend() because Vim buffers do not support it.
    for line in signature:
        buffer.append(line)
