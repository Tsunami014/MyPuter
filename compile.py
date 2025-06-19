#!/bin/python3
import argparse
from dataclasses import dataclass
import re
from abc import ABC, abstractmethod
from enum import IntEnum
from parsimonious.grammar import Grammar

REG_KEY = {
    "NULL": -1,
    "O":   0,
    "OUT": 0,
    "A": 1,
    "B": 2,
    "RAM": 5, # TODO: add to actual device
    "DA": 6 # TODO: add to actual device
}
def parseNum(num):
    num = num.lower()
    if num[:2] == '0x':
        return int(num, 16)
    elif num[:2] == '0b':
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
    __slots__ = ['fromR', 'toR', 'addr']
    typ = NodeTypes.READWRITE
    def __init__(self, node, _):
        c = node.children[0]
        toR, _, fromR = (i.text for i in c.children[0].children)
        if node.expr_name == 'ReadWriteFrom':
            fromR, toR = toR, fromR
        
        if fromR[1] in '0123456789':
            self.fromR = parseNum(fromR[1:])
        else:
            self.fromR = REG_KEY[fromR.upper()[1:]]
        if toR[1] in '0123456789':
            self.toR = parseNum(toR[1:])
        else:
            self.toR = REG_KEY[toR.upper()[1:]]
        
        if node.children[1].text == '':
            self.addr = -1
        else:
            self.addr = parseNum(node.children[1].text[1:])
    
    def toBasic(self):
        if self.fromR == REG_KEY['A']:
            return [BasicOp(-1, REG_KEY['OUT'], 0b11111), BasicOp(REG_KEY['OUT'], self.toR, self.addr)] # If reading from A, write to out using ALU instruction 'output A', then use the out register for reading
        if self.fromR == REG_KEY['B']:
            return [BasicOp(-1, REG_KEY['OUT'], 0b10101), BasicOp(REG_KEY['OUT'], self.toR, self.addr)] # Same with B
        return [BasicOp(self.fromR, self.toR, self.addr)]

    def __str__(self):
        addrStr = ""
        if self.addr != -1:
            addrStr = f" with addr {self.addr}"
        return f'Set register {self.toR} to register {self.fromR}{addrStr}'
    def __repr__(self):
        return f'<{self.__str__()}>'

class ReadWriteAssgn(Node):
    __slots__ = ['fromS', 'toR', 'addr']
    typ = NodeTypes.READWRITE
    def __init__(self, node, _):
        c = node.children[0]
        toR, _, fromS = (i.text for i in c.children[0].children)
        if node.expr_name == 'ReadWriteFrom':
            fromS, toR = toR, fromS
        
        self.toR = REG_KEY[toR.upper()[1:]]
        typ = c.children[0].children[2].children[0].expr_name
        if typ == 'num':
            self.fromS = (parseNum(fromS), 'num')
        else: # var
            if fromS[0] == '@':
                self.fromS = (parseNum(fromS[1:]), 'addr')
            else:
                assert fromS in vars, f"Variable {fromS} does not exist in the current scope!"
                raise NotImplementedError('No variables allowed yet :(')
        
        if node.children[1].text == '':
            self.addr = -1
        else:
            self.addr = parseNum(node.children[1].text[1:])
    
    def toBasic(self):
        if self.addr == -1:
            if self.fromS[1] == 'addr':
                return [BasicOp(self.fromS[0], self.toR, self.addr)]
            else: # num
                return [BasicOp(-1, REG_KEY['DA'], self.fromS[0]), BasicOp(REG_KEY['DA'], self.toR, self.addr)]
        raise NotImplementedError(
            "Cannot use address in => yet, sry"
        ) # TODO: This

    def __str__(self):
        addrStr = ""
        if self.addr != -1:
            addrStr = f" with addr {self.addr}"
        return f'Set register {self.toR} to {"@" if self.fromS[1] == "addr" else ""}{self.fromS[0]}{addrStr}'
    def __repr__(self):
        return f'<{self.__str__()}>'

class Assign(Node):
    __slots__ = ['fromA', 'toA']
    typ = NodeTypes.ASSIGN
    def __init__(self, node, parents):
        raise NotImplementedError("Not implemented") # TODO: Fix this class
        vars = [var for i in parents for var in i.vars]
        for idx, n in enumerate(node.children):
            if idx == 1:
                continue
            start = n.text
            typ = n.children[0].expr_name
            if typ == 'num':
                end = parseNum(start)
            else: # var
                if start[0] == '@':
                    end = parseNum(start[1:])
                else:
                    assert start in vars, f"Variable {start} does not exist in the current scope!"
                    raise NotImplementedError('No variables allowed yet :(')
            
            if idx == 0:
                self.toA = end
            else:
                self.fromA = end
    
    def toBasic(self):
        # Set A to contents of register at specified address, output A to the out register through the ALU, then read from that to write to the other RAM address
        # Maybe TODO: add another register to make this 2 steps instead of 3
        return [BasicOp(REG_KEY['RAM'], REG_KEY['A'], self.fromA), BasicOp(-1, REG_KEY['OUT'], 0b11111), BasicOp(REG_KEY['OUT'], REG_KEY['RAM'], self.toA)]

    def __str__(self):
        return f'Set @{self.toA} to @{self.fromA}'
    def __repr__(self):
        return f'<@{self.toA} = @{self.fromA}>'

STATEMENT_PARSERS = {
    'NOOP': NOOP,
    'ReadWrite': ReadWrite,
    'ReadWriteAssgn': ReadWriteAssgn,
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
    def parseOp(op: BasicOp, parentLabel: Label, args: argparse.Namespace):
        pass

    @abstractmethod
    def parseLabels(parseds, args: argparse.Namespace):
        pass

class ParseToArduino(BaseParser):
    def parseOp(op: BasicOp, parentLabel: Label, args: argparse.Namespace):
        out = []
        read = op.read != -1
        write = op.write != -1
        writeTo = None
        if args.arduino_optimise:
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

    def parseLabels(parseds, args: argparse.Namespace):
        out = ['#include "base.h"\n#include "Code.h"']
        if args.arduino_optimise:
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

def parseWithParser(labls, parser, args):
    out = {}
    for labl in labls:
        out[labl] = "".join(parser.parseOp(i, labl, args) for i in labl.toBasic())
    return parser.parseLabels(out, args)

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

    parser.add_argument(
        '-AO', '--arduino-optimise',
        action='store_true',
        help="Use the arduino for storing RAM and the direct address instead of the actual chips."
    )

    args = parser.parse_args()

    with open(args.file) as f:
        fc = f.read()
    
    out = parse(fc)
    outfc = parseWithParser(out, ParseToArduino, args)
    with open('Code.cpp', 'w+') as f:
        f.write(outfc)

if __name__ == "__main__":
    main()
