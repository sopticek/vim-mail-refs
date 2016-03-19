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
    current_line = buffer[row]
    before_pos = current_line[:col + 1]
    after_pos = current_line[col + 1:]
    new_line = before_pos + ref + after_pos
    buffer[row] = new_line
    if col == 0:
        col = -1
    return row, col + len(ref)


def _append_ref_url(buffer, ref_url):
    refs = _get_refs_with_urls(buffer)
    ref = '[{}]'.format(len(refs) + 1)
    if not refs:
        buffer.append('')
    buffer.append('{} {}'.format(ref, ref_url))
    return ref


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
