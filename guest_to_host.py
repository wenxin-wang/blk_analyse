#!/usr/bin/env python3

import sys, argparse
import range

arg_parser = argparse.ArgumentParser(description='Tranlate blkparse output into a table of records.')
arg_parser.add_argument('--host', help='Set host block file')
arg_parser.add_argument('--guest', help='Set guest block file')
args = arg_parser.parse_args()

block_range = range.ranges()
with open(args.host, encoding='utf-8') as hostblocks:
    block_range.read(hostblocks)
l = block_range.split_logic(12,4376825)
print(l)
s = 0
for r in l:
    s += r[1]
print(s)
