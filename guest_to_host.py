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
        return "{}-{}".format(self.first, self.last)
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
    def map(self, logic):
        """Find the physic location for logic block"""
        for r in self.ranges:
            if logic < r.length:
                return r.first + logic
            else:
                logic -= r.length
        raise ValueError('Range doesn\'t contain logic block {}'.format(logic+1))

block_range = ranges()
with open(args.host, encoding='utf-8') as hostblocks:
    block_range.read(hostblocks)
r = (block_range.find_range(block_range.map(4474880)))
print(r)
print(r.contain(726597632))
