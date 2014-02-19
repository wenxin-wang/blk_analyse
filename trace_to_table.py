#!/usr/bin/env python3

# The python version for translating blkparse output into a table. Each row in a table is a record of the time stamps of a request, in this format:
# Offset+Length A(map time) Q(queue time) G(get time) I(insert time) D(driver time) M(merged time) C(complete time)
# A record can't have both M and C time.
# Arguments:
# i:input o:output O:offset

import sys, argparse
import record

arg_parser = argparse.ArgumentParser(description='Tranlate blkparse output into a table of records.')
arg_parser.add_argument('-hi', dest='hparse', help='Set host blkparse file')
arg_parser.add_argument('-gi', dest='gparse', help='Set guest blkparse file')
arg_parser.add_argument('-o', dest='output', help='Set output file')
arg_parser.add_argument('-hO', dest='hoffset', type=int, default=0, help='Set host offset')
arg_parser.add_argument('-gO', dest='goffset', type=int, default=0, help='Set guest offset')
arg_parser.add_argument('-htsec', type=int, default=0, help='Set the sec part of host time offset')
arg_parser.add_argument('-htnsec', type=int, default=0, help='Set the nanosec part of host time offset')
arg_parser.add_argument('-gtsec', type=int, default=0, help='Set the sec part of guest time offset')
arg_parser.add_argument('-gtnsec', type=int, default=0, help='Set the nanosec part of guest time offset')
arg_parser.add_argument('--hblock', help='Set host block file')
arg_parser.add_argument('--gblock', help='Set guest block file')
args = arg_parser.parse_args()

outfile = open(args.output, encoding='utf-8') if args.output else sys.stdout

h_block_range = record.ranges()
with open(args.hblock, encoding='utf-8') as hostblocks:
    h_block_range.read(hostblocks)

g_block_range = record.ranges()
with open(args.gblock, encoding='utf-8') as guestblocks:
    g_block_range.read(guestblocks)

ht = record.table()
with open(args.hparse, encoding='utf-8') as hinput:
    ht.read_records(hinput, args.hoffset, time_offset=record.time(args.htsec, args.htnsec))
ht.filter(h_block_range)

gt = record.table()
with open(args.gparse, encoding='utf-8') as ginput:
    gt.read_records(ginput, args.goffset, time_offset=record.time(args.gtsec, args.gtnsec))
#gt.print_table(outfile)
print('*' * 40)
gt.filter(g_block_range)

print('*' * 40)
#gt.print_table(outfile)
grs = h_block_range.split(gt)
print('#' * 40)
print(h_block_range.split_logic(0, 8))
print(h_block_range.split_logic(4999168, 8))
print(h_block_range.split_logic(4999176, 8))
print(h_block_range.find_block(721801471))
#ht.print_table(outfile)
#gt.print_table(outfile)
#grs.print_maps()
print('#' * 40)
x=grs.gen_r2r_maps(ht)
print('#' * 40)
for i in x:
    print(i[0], '\n | ', i[1])
