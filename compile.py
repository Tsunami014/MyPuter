#!/bin/python3
import argparse
from dataclasses import dataclass
import re
from abc import ABC, abstractmethod
from enum import IntEnum
from parsimonious.grammar import Grammar

REG_KEY = {
    "NULL": -1,# Do nothing
    "O":   0,# Output from the ALU
    "OUT": 0,# The same as before
    "A": 1,  # Input 1 to the ALU
    "B": 2,  # Input 2 to the ALU
    "RAM": 4,# The RAM chip address
    "X": 5,  # A simple register
    "DA": 6 # TODO: add to actual device
    # Add an address to data (Direct Address) and data to address (Pointer/indexing? register)
}

# The list of registers for the arduino to fake the existance of. Only use ones in this list.
FAKE = {
    'DA': True
}



def parseNum(num):
    num = num.lower()
    if num[0] == '$':
        return int(num[1:], 16)
    if num[0] == '&':
        return int(num[1:], 2)
    if num[:2] == '0x':
        return int(num, 16)
    if num[:2] == '0b':
        return int(num, 2)
    return int(num)

class NodeTypes(IntEnum):
    LABEL = -1
    NOOP = 0
    READWRITE = 1
    ASSIGN = 2


@dataclass(slots=True)
class BasicOp:
    read: int
    write: int
    addr: int

class Node(ABC):
    __slots__ = ['typ']
    typ: NodeTypes

    @abstractmethod
    def toBasic(self) -> list[BasicOp]:
        pass

class Label(Node):
    __slots__ = ['name', 'children', 'vars', 'allLabls']
    typ = NodeTypes.LABEL
    def __init__(self, node, parents):
        self.name = node.children[0].text
        if any(p.name == self.name for p in parents):
            raise ValueError(
                f'Multiple definitions of label {self.name}!'
            )
        self.vars = [var for i in parents for var in i.vars]
        self.vars.extend(n.children[1].text for n in node.children[2].children)
        self.children = []
        self.allLabls = [self]
        for n2 in node.children[3].children:
            n = n2.children[0]
            nme = n.expr_name
            if nme == 'label_block':
                self.allLabls.extend(Label(n, parents+[self]).allLabls)
            elif nme == 'statement':
                self.children.append(Statement(n.children[0], parents+[self]))
            else:
                raise ValueError(
                    f'Node with name "{nme}" should not be here! Node text: {node.text}'
                )
    
    def toBasic(self):
        return [i for s in self.children for i in s.toBasic()]
    
    def __str__(self):
        return f'Label {self.name} with vars {self.vars}'
    def __repr__(self):
        return f'<Label "{self.name}" with {len(self.children)} statements>'

class NOOP(Node):
    typ = NodeTypes.NOOP
    def __init__(self, _, __):
        pass
    def toBasic(self):
        return [BasicOp(-1, -1, -1)]
    def __str__(self):
        return 'NOOP'
    def __repr__(self):
        return '<NOOP>'

class ReadWrite(Node):
    __slots__ = ['fromS', 'toS', 'addr']
    typ = NodeTypes.READWRITE
    def __init__(self, node, _):
        c = node.children[0]
        toN, _, fromN = c.children[0].children
        if node.expr_name == 'ReadWriteFrom':
            fromN, toN = toN, fromN
        
        for n, toV in (
            (fromN, 'fromS'),
            (toN, 'toS')
        ):
            typ = n.expr_name
            if typ == 'ReadWriteOps':
                typ = n.children[0].expr_name
            if typ == 'AssignOpts':
                typ = n.children[0].children[0].expr_name
            self._handle(n.text, typ, toV)

        if node.children[1].text == '':
            self.addr = -1
        else:
            self.addr = parseNum(node.children[1].text[1:])

    def _handle(self, txt, typ, toV):
        if typ == 'num':
            out = (parseNum(txt), 'num')
        elif typ == 'NULL':
            out = (None, 'null')
        elif typ == 'register':
            if txt[1] in '0123456789':
                out = (parseNum(txt[1:]), 'reg')
            else:
                if txt[1:] not in REG_KEY:
                    raise ValueError(
                        f'Register {txt} not found!'
                    )
                out = (REG_KEY[txt[1:]], 'reg')
        elif typ == 'var':
            if txt[0] == '@':
                out = (parseNum(txt[1:]), 'ram')
            else:
                raise NotImplementedError('Variables not supported yet!')
                #out = (Variables_to_addrs[txt], 'ram')
        setattr(self, toV, out)
    
    def toBasic(self):
        s = []
        addr = None
        if self.fromS[1] == 'null':
            rd = -1
        elif self.fromS[1] == 'num':
            s = [BasicOp(-1, REG_KEY['DA'], self.fromS[0])]
            rd = REG_KEY['DA']
        elif self.fromS[1] == 'reg':
            if self.fromS[0] == REG_KEY['A']:
                rd = REG_KEY['OUT']
                s = [BasicOp(-1, REG_KEY['OUT'], 0b11111)] # If reading from A, write to out using ALU instruction 'output A', then use the out register for reading
            elif self.fromS[0] == REG_KEY['B']:
                rd = REG_KEY['OUT']
                s = [BasicOp(-1, REG_KEY['OUT'], 0b10101)] # Same with B
            else:
                rd = self.fromS[0]
        elif self.fromS[1] == 'ram':
            addr = self.fromS[0]
            rd = REG_KEY['RAM']
        else:
            raise ValueError(
                f'FromS type not found: "{self.fromS[1]}"'
            )

        addr2 = None
        if self.toS[1] == 'null':
            wr = -1
        elif self.toS[1] == 'reg':
            wr = self.toS[0]
        elif self.toS[1] == 'ram':
            wr = REG_KEY['RAM']
            addr2 = self.toS[0]
        else:
            raise ValueError(
                f'ToS type not found: "{self.toS[1]}"'
            )
        if addr is not None and self.addr is not None:
            raise ValueError(
                f'Address specified in this instruction "{self.addr}" conflicts with instruction which requires an address of {addr}. Please remove the address from this instruction.'
            )
        addr2 = (addr2 if addr2 is not None else self.addr) # The output addr is whatever is set; as now, only one can be
        if addr is not None and addr2 is not None:
            return s + [BasicOp(rd, REG_KEY['A'], addr), BasicOp(REG_KEY['A'], wr, addr2)]
        # HACK: This relies heavily on the address being used for the correct purpose.
        #       If the address is set due to an instruction, it *may* be right. If it's set by the dev, it may/may not be right, depending on how good the programmer is.
        return s + [BasicOp(rd, wr, (addr if addr is not None else addr2))]

    def __str__(self):
        addrStr = ""
        if self.addr != -1:
            addrbin = "{0:b}".format(self.addr).rjust(8, "0")
            addrStr = f" with addr {self.addr} ({addrbin})"
        return f'Set {self.toS[1]} {self.toS[0]} to {self.fromS[1]} {self.fromS[0]}{addrStr}'
    def __repr__(self):
        return f'<{self.__str__()}>'

class Assign(ReadWrite):
    def __init__(self, node, _):
        toN, _, fromN = node.children
        if node.expr_name == 'ReadWriteFrom':
            fromN, toN = toN, fromN
        
        for n, toV in (
            (fromN, 'fromS'),
            (toN, 'toS')
        ):
            typ = n.children[0].expr_name
            self._handle(n.text, typ, toV)

        self.addr = -1


STATEMENT_PARSERS = {
    'NOOP': NOOP,
    'ReadWrite': ReadWrite,
    'Assign': Assign,
}
def Statement(node, parents):
    n = node.children[0]
    nme = n.expr_name
    if nme in STATEMENT_PARSERS:
        return STATEMENT_PARSERS[nme](n, parents)
    else:
        raise ValueError(
            f'Node with name "{nme}" should not be here! Node text: {n.text}'
        )


class BaseParser(ABC):
    __slots__ = []
    @abstractmethod
    def parseOp(op: BasicOp, parentLabel: Label):
        pass

    @abstractmethod
    def parseLabels(parseds):
        pass

class ParseToArduino(BaseParser):
    def parseOp(op: BasicOp, parentLabel: Label):
        out = []
        read = op.read != -1
        write = op.write != -1
        writeTo = None
        if FAKE['DA']:
            if op.read == REG_KEY['DA']:
                if op.write == REG_KEY['DA']:
                    raise ValueError(
                        'Cannot read and write to the DA with arduino optimisation!'
                    )
                out.append("writeData(DA);")
                read = False
            if op.write == REG_KEY['DA']:
                writeTo = 'DA'
                write = False
        if read:
            out.append(f"setreadAddr({op.read});")
        if write:
            out.append(f"setwriteAddr({op.write});")
        if op.addr != -1:
            out.append(f"writeAddr({op.addr});")
        if writeTo is None:
            out.extend([
                "Apply();",
                "delay(waitTime);",
                # "printData();",
                "Reset();"
            ])
        else:
            out.extend([
                "Apply();",
                "delay(waitTime);",
                writeTo + " = getData();",
                "Reset();"
            ])
        return "    "+"\n    ".join(out)+"\n"

    def parseLabels(parseds):
        out = ["""
// This file was autogenerated by `compile.py` and will be overwritten on subsequent runs.
#include "base.h"
#include "Code.h"
"""[1:-1]]
        if FAKE['DA']:
            out.append("uint8_t DA;")
        for l, parsed in parseds.items():
            nme = l.name
            if nme == 'loop':
                nme = 'main_tick'
            elif nme == 'init':
                nme = 'main_init'
            else:
                nme = '_'+nme
            out.append("void "+nme+"() {\n"+parsed+"}")
        return "\n\n".join(out)+"\n"


def printParsed(node, ind=0):
    spacing = '  '*ind
    childr = getattr(node, 'children', [])
    if childr != []:
        end = ":"
    else:
        end = ""
    print(spacing + str(node) + end)
    for c in childr:
        printParsed(c, ind+1)

def parseWithParser(labls, parser):
    out = {}
    for labl in labls:
        out[labl] = "".join(parser.parseOp(i, labl) for i in labl.toBasic())
    return parser.parseLabels(out)

INLINE_COMMENT = r"#>(?:\\.|[^\\<\n]|<[^#\n])*?(?:<#|[<\\]?\n)"
MULTILINE_COMMENT = r"#>>(?:\\.|[^\\<]|<(?!!<#))*?<<#"
def parse(fc):
    fixed = re.sub(INLINE_COMMENT, "", re.sub(MULTILINE_COMMENT, "", fc)).replace(" ", "").replace("\t", "").replace("\n", "")
    with open('lang') as f:
        g = Grammar(f.read())
    parsed = g.parse(fixed)

    assert parsed.expr_name == 'file'

    parsedN = []
    for n in parsed.children:
        nme = n.expr_name
        if nme == 'label_block':
            parsedN.extend(Label(n, []).allLabls)
        elif nme == 'statement':
            raise ValueError(
                f'Statements must be under a label! Statement text: {n.text}'
            )
        else:
            raise ValueError(
                f'Node with name "{nme}" should not be here! Node text: {n.text}'
            )

    for node in parsedN:
        printParsed(node)

    return parsedN

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'file',
        nargs='?',
        default='./code/main.tn',
        help="Path to the file to compile (default: ./code/main.tn)"
    )

    args = parser.parse_args()

    with open(args.file) as f:
        fc = f.read()
    
    out = parse(fc)
    outfc = parseWithParser(out, ParseToArduino)
    with open('Code.cpp', 'w+') as f:
        f.write(outfc)

if __name__ == "__main__":
    main()
