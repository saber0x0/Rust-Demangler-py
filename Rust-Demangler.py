#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/08/04 15:10
# @Author  : Mans00r
# @File    : 1.py

import sys

HASH_LEN = 16
HASH_PREFIX = "::h"


def unescape(input_str, output, sequence, value):
    if input_str.startswith(sequence):
        output.append(value)
        input_str = input_str[len(sequence):]
        return True
    return False


def strip_symbol_prefix_legacy(sym):
    if sym.startswith("__ZN"):
        return sym[len("__ZN"):]
    if sym.startswith("_ZN"):
        return sym[len("_ZN"):]
    return sym.lstrip("ZN")


def rust_demangle_symbol_element_legacy(legacy_symbol_element):
    output = []
    i = 0
    last_char = '\0'
    for c in legacy_symbol_element:
        if c == '$':
            if (unescape(legacy_symbol_element[i:], output, "$C$", ',')
                    or unescape(legacy_symbol_element[i:], output, "$SP$", '@')
                    or unescape(legacy_symbol_element[i:], output, "$BP$", '*')
                    or unescape(legacy_symbol_element[i:], output, "$RF$", '&')
                    or unescape(legacy_symbol_element[i:], output, "$LT$", '<')
                    or unescape(legacy_symbol_element[i:], output, "$GT$", '>')
                    or unescape(legacy_symbol_element[i:], output, "$LP$", '(')
                    or unescape(legacy_symbol_element[i:], output, "$RP$", ')')
                    or unescape(legacy_symbol_element[i:], output, "$u20$", ' ')
                    or unescape(legacy_symbol_element[i:], output, "$u22$", '\"')
                    or unescape(legacy_symbol_element[i:], output, "$u27$", '\'')
                    or unescape(legacy_symbol_element[i:], output, "$u2b$", '+')
                    or unescape(legacy_symbol_element[i:], output, "$u3b$", ';')
                    or unescape(legacy_symbol_element[i:], output, "$u5b$", '[')
                    or unescape(legacy_symbol_element[i:], output, "$u5d$", ']')
                    or unescape(legacy_symbol_element[i:], output, "$u7b$", '{')
                    or unescape(legacy_symbol_element[i:], output, "$u7d$", '}')
                    or unescape(legacy_symbol_element[i:], output, "$u7e$", '~')):
                continue
            else:
                raise ValueError(f"invalid legacy symbol element {legacy_symbol_element}")
        elif c == '.' and i + 1 < len(legacy_symbol_element) and legacy_symbol_element[i + 1] == '.':
            output.append("::")
            i += 2
        elif c == '_' and (i == 0 or last_char == ':') and i + 1 < len(legacy_symbol_element) and legacy_symbol_element[
            i + 1] == '$':
            i += 2
        else:
            output.append(c)
            i += 1
        last_char = c
    return ''.join(output)


def split_symbol_into_elements_legacy(legacy_symbol):
    cursor = 0
    elements = []
    end = len(legacy_symbol) - (len(HASH_PREFIX) + HASH_LEN) - 1
    i = 0
    while i < end:
        if legacy_symbol[i].isdigit():
            cursor = cursor * 10 + int(legacy_symbol[i])
            i += 1
        else:
            elements.append(legacy_symbol[i:i + cursor])
            i += cursor
            cursor = 0
    return elements


def demangle_symbol_legacy(legacy_symbol):
    if not (len(legacy_symbol) > 1 and legacy_symbol[-1] == 'E'):
        return legacy_symbol
    legacy_symbol_stripped = strip_symbol_prefix_legacy(legacy_symbol)
    if legacy_symbol_stripped is None:
        return legacy_symbol
    legacy_symbol_elements = split_symbol_into_elements_legacy(legacy_symbol_stripped)
    legacy_elements_demangled = [rust_demangle_symbol_element_legacy(e) for e in legacy_symbol_elements]
    return "::".join(legacy_elements_demangled)


def main():
    if len(sys.argv) < 2:
        for line in sys.stdin:
            print(demangle_symbol_legacy(line.strip()))
    else:
        for rust_symbol in sys.argv[1:]:
            print(demangle_symbol_legacy(rust_symbol))


# _$LT$$LT$alloc..boxed..Box$LT$dyn$u20$core..error..Error$u2b$core..marker..Sync$u2b$core..marker..Send$GT$$u20$as$u20$core..convert..From$LT$alloc..string..String$GT$$GT$..from..StringError$u20$as$u20$core..error..Error$GT$::description::hb7eee83313c55e7a
# _ZN4core3fmt8builders11DebugStruct5field17h57f07a8fd6789081E
# _ZN4core3fmt3num3imp54_$LT$impl$u20$core..fmt..Display$u20$for$u20$usize$GT$3fmt17h122e9759da83063eE
# _ZN4core9panicking19panic_cannot_unwind17h28642020a763cc3eE
# _ZN57_$LT$core..fmt..Arguments$u20$as$u20$core..fmt..Debug$GT$3fmt17h1d49834e52540305E
if __name__ == "__main__":
    main()
