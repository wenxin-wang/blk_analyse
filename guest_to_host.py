#!/usr/bin/env python3

import sys, argparse

arg_parser = argparse.ArgumentParser(description='Tranlate blkparse output into a table of records.')
arg_parser.add_argument('--host', help='Set host block file')
arg_parser.add_argument('--guest', help='Set guest block file')
args = arg_parser.parse_args()

class range:
    def __init__(self, first, last):
        """Initialize range"""
        if(first > last):
            raise ValueError('First block in range must not be larger than the last one')
        self.first = first
        self.last = last
        self.length = self.last - self.first + 1
    def __str__(self):
        """Stringlize range"""
        return "{}-{} {}".format(self.first, self.last, self.length)
    def contain(self, value):
        """Find if a block is within range"""
        return value >= self.first and value <= self.last

class ranges:
    def __init__(self):
        """Initialize range"""
        self.ranges = []
    def __str__(self):
        """Stringlize ranges"""
        string = '\n'.join([str(r) for r in self.ranges])
        return string
    def read(self, fd):
        """Read from fd"""
        for line in fd:
            line = line.split('-')
            self.ranges.append(range(int(line[0]), int(line[1])))
    def find_range(self, block):
        """Find the range a block belongs"""
        for r in self.ranges:
            if r.contain(block):
                return r
        raise ValueError('Ranges doesn\'t contain block {}'.format(block))
    def split_logic(self, offset, length):
        """Split offset+length into a list"""
        list = []
        for r in self.ranges:
            if offset < r.length:
                left = r.first + offset
                if r.last - left + 1 >= length:
                    list.append([left, length, str(r)])
                    length = 0
                    return list
                else:
                    lth = r.last - left + 1
                    list.append([left, lth, str(r)])
                    offset = 0
                    length -= lth
            else:
                offset -= r.length
        if length > 0:
            raise ValueError('Ranges couldn\'t map all the blocks')
        return list

    def map(self, logic):
        """Find the physic location for logic block"""
        for r in self.ranges:
            if logic < r.length:
                return r.first + logic
            else:
                logic -= r.length
        raise ValueError('Ranges doesn\'t contain logic block {}'.format(logic+1))

block_range = ranges()
with open(args.host, encoding='utf-8') as hostblocks:
    block_range.read(hostblocks)
l = block_range.split_logic(12,4376825)
print(l)
s = 0
for r in l:
    s += r[1]
print(s)
