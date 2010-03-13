#!/usr/bin/env python
'''
Simple script to substitute variables for color values into a CSS file.

Takes a "base" CSS file (which is just normal CSS with "variables" sprinkled
in) and a mappings file, which defines the values for the substitutions to
take.

Care should be made with variable names, as they are blindly replaced throughout
the entire file (case-sensitive, and only if surrounded by word boundaries).
'''

import re
import sys

def replace_all(text, mappings):
    for regex, val in mappings:
        text = regex.sub(val, text)
    return text

MAPPING = re.compile(r'^(\w+): (#?\w+)$')
def read_mappings(file):
    mappings = []
    for line in open(file):
        match = MAPPING.match(line)
        if match:
            var, val = match.groups()
            regex = re.compile(r'\b%s\b' % re.escape(var))
            mappings.append( (regex, val) )
    return mappings

def replace(mappings_file, base_file=None, out_file=None):
    if isinstance(base_file, basestring):
        base_file = open(base_file)
    elif not base_file:
        base_file = sys.stdin

    if isinstance(out_file, basestring):
        out_file = open(out_file, 'w')
    elif not out_file:
        out_file = sys.stdout

    mappings = read_mappings(mappings_file)
    subbed = replace_all(base_file.read(), mappings)

    out_file.write(subbed)


def main():
    args = { 'mappings_file': sys.argv[1] }

    if len(sys.argv) > 2 and sys.argv[2] != '-':
        args['base_file'] = sys.argv[2]

    if len(sys.argv) > 3 and sys.argv[3] != '-':
        args['out_file'] = sys.argv[3]

    replace(**args)

if __name__ == '__main__':
    main()
