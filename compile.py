#!/bin/python3
import argparse
import re
from parsimonious.grammar import Grammar

from abc import ABC
from typing import List

class Node(ABC):
    __slots__ = ['children']
    children: List

class Label(Node):
    __slots__ = ['name', 'children']
    def __init__(self, node):
        self.name = node.children[0].text
        self.children = [parseTree(n.children[0]) for n in node.children[2].children]
    
    def __str__(self):
        return f'Label {self.name}'
    def __repr__(self):
        return f'<Label "{self.name}" with {len(self.children)} statements>'

class Statement(Node):
    __slots__ = ['txt', 'children']
    def __init__(self, node):
        self.txt = node.text[:-1]
        self.children = []
    
    def __str__(self):
        return 'Statement; '+self.txt
    def __repr__(self):
        return f'<Statement; {self.txt}>'

PARSERS = {
    'label_block': Label,
    'statement': Statement
}
def parseTree(node):
    nme = node.expr_name
    if nme in PARSERS:
        return PARSERS[nme](node)
    else:
        raise ValueError(
            f'Node with name "{nme}" should not be here! Node text: {node.text}'
        )

def printParsed(node, ind=0):
    spacing = '  '*ind
    if node.children != []:
        end = ":"
    else:
        end = ""
    print(spacing + str(node) + end)
    for c in node.children:
        printParsed(c, ind+1)

INLINE_COMMENT = r"#>(?:\\.|[^\\<\n]|<[^#\n])*?(?:<#|[<\\]?\n)"
MULTILINE_COMMENT = r"#>>(?:\\.|[^\\<]|<(?!!<#))*?<<#"
def parse(fc):
    fixed = re.sub(INLINE_COMMENT, "", re.sub(MULTILINE_COMMENT, "", fc)).replace(" ", "").replace("\t", "").replace("\n", "")
    with open('lang') as f:
        g = Grammar(f.read())
    parsed = g.parse(fixed)
    assert parsed.expr_name == 'file'
    parsedN = [parseTree(n) for n in parsed.children]
    for n in parsedN:
        printParsed(n)
    return parsedN

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'file',
        nargs='?',
        default='./code/main.tn',
        help="Path to the file to compile (default: ./code/main.tn)"
    )

    parser.add_argument(
        '-AR', '--arduino-ram',
        action='store_true',
        help="Use the arduino for storing RAM instead of the RAM chip"
    )

    args = parser.parse_args()

    with open(args.file) as f:
        fc = f.read()
    
    parse(fc)

if __name__ == "__main__":
    main()
