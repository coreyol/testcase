# -*- coding: utf-8 -*-
"""
    strutil.py
"""

import sys
# import unicodedata

import colorama


def fitlength(s, maxlen=sys.maxsize, ommission_text = '...'):
    """
    Fits string length to the given length.

    :params: s: A string.
    :params: maxlen: Maximum length for the fitted string.
    :params: ommission_text: The text to be inserted to indicate ommitted parts.

    :returns: A string of which length is fitted accordingly.
    """

    if type(s) is not str:
        s = str(s)

    if len(s) <= maxlen:
        return s

    # maxlen == start_len + len('...') + len(middle part) + len('...') + end_len
    # start_len == len(middle part) == end_len ~= (maxlen - len('...') * 2) / 3
    segments_length = (maxlen - len(ommission_text) * 2) // 3
    return ommission_text.join([s[:segments_length], s[(maxlen - segments_length) // 2:(maxlen + segments_length) // 2], s[-segments_length:]])

def colorize(s, color):
    return f'{color}{s}{colorama.Style.RESET_ALL}'

def append_lateral_lines(lines, insert_index, append_lines, lateral_spaces=5):
    """
    Inserts append_lines laterally to lines beginning from the insert_index'th line.
    """

    # if insert_index >= len(lines):
    #     for _ in range(insert_index - len(lines)):
    #         lines.append('')

    # if len(lines) < insert_index + len(append_lines):
    #     for _ in range(insert_index + len(append_lines) - len(lines)):
    #         lines.append('')

    for _ in range(insert_index + len(append_lines) - len(lines)):
        lines.append('')

    table_start_position = max(map(len, lines[insert_index:insert_index + len(append_lines)])) + lateral_spaces
    for i in range(len(append_lines)):
        lines[insert_index + i] = lines[insert_index + i] + ' ' * (table_start_position - len(lines[insert_index + i])) + append_lines[i]

    return lines

# def repr_unquote(s: str) -> str:
#     """Returns repr(s) without quotations.
#     """
#     return repr(s)[1:-1]

# def terminal_display_width(s: str) -> int:
#     """Returns display length of a string :s:.
#     Handles both "wide" multibyte characters (such as CJK) and zero-width characters.
    
#     ref. https://stackoverflow.com/q/48598304

#     see:
#     https://stackoverflow.com/questions/34655347/formatting-columns-containing-non-ascii-characters
#     https://stackoverflow.com/questions/22225441/display-width-of-unicode-strings-in-python
#     """
#     width = 0
#     for c in s:
#         # For zero-width characters
#         if unicodedata.category(c)[0] in ('M', 'C'):
#             continue
#         w = unicodedata.east_asian_width(c)
#         if w in ('N', 'Na', 'H', 'A'):
#             width += 1
#         else:
#             width += 2

#     return width
