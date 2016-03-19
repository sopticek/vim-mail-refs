#
# Author:   Daniela Duricekova <daniela.duricekova@gmail.com>
# Date:     2016-03-18
#

import re


def add_ref(buffer, window, ref_url):
    row, col = _get_cursor_pos(window)
    ref = _append_ref_url(buffer, ref_url)
    row, col = _insert_ref(buffer, row, col, ref)
    _set_cursor_pos(window, row, col)


def _insert_ref(buffer, row, col, ref):
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


def _append_ref_url(buffer, ref_url):
    refs = _get_refs_with_urls(buffer)
    ref = '[{}]'.format(len(refs) + 1)
    if not refs:
        buffer.append('')
    buffer.append('{} {}'.format(ref, ref_url))
    return ref


def _prepare_line_for_ref_insert(line, col):
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
    refs = []
    for line in reversed(buffer):
        m = re.match(r'(\[\d+\]) (.+)', line)
        if m is None:
            break
        refs.append(m.groups())
    return refs


def _get_cursor_pos(window):
    row, col = window.cursor
    return row - 1, col


def _set_cursor_pos(window, row, col):
    window.cursor = (row + 1, col)
