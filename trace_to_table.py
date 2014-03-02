#!/usr/bin/env python3

# The python version for translating blkparse output into a table. Each row in a table is a record of the time stamps of a request, in this format:
# Offset+Length A(map time) Q(queue time) G(get time) I(insert time) D(driver time) M(merged time) C(complete time)
# A record can't have both M and C time.
# Arguments:
# i:input o:output O:offset

import sys, argparse, csv
from lib import record

arg_parser = argparse.ArgumentParser(description='Tranlate blkparse output into a table of records.')
arg_parser.add_argument('-hi', dest='hparse', help='Set host blkparse file')
arg_parser.add_argument('-gi', dest='gparse', help='Set guest blkparse file')
arg_parser.add_argument('-o', dest='output', help='Set output file')
arg_parser.add_argument('-hO', dest='hoffset', type=int, default=0, help='Set host offset')
arg_parser.add_argument('-gO', dest='goffset', type=int, default=0, help='Set guest offset')
arg_parser.add_argument('-htfile', help='Set host time offset file')
arg_parser.add_argument('-gtfile', help='Set guest time offset file')
arg_parser.add_argument('-gtnsec', help='Set the nanosec part of guest time offset')
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

if args.htfile:
    with open(args.htfile) as f:
        htime = record.time.from_str(f.readline())
else: htime = record.time(0, 0)

if args.gtfile:
    with open(args.gtfile) as f:
        gtime = record.time.from_str(f.readline())
else: gtime = record.time(0, 0)

if htime > gtime:
    htime_gap = record.time(0, 0)
    gtime_gap = htime - gtime
else:
    htime_gap = gtime - htime
    gtime_gap = record.time(0, 0)

ht = record.table()
with open(args.hparse, encoding='utf-8') as hinput:
    ht.read_records(hinput, args.hoffset, time_offset=htime_gap)
ht.filter(h_block_range)

gt = record.table()
with open(args.gparse, encoding='utf-8') as ginput:
    gt.read_records(ginput, args.goffset, time_offset=gtime_gap)
#gt.print_table(outfile)
print('*' * 40)
gt.filter(g_block_range)

print('*' * 40)
#gt.print_table(outfile)
grs = h_block_range.split(gt)
x=grs.gen_r2r_maps(ht)
print('#' * 40)

with open('times.csv', 'w', newline='') as timesf, open('gaps.csv', 'w', newline='') as gapsf:
    times_writer = csv.writer(timesf)
    gaps_writer = csv.writer(gapsf)
    fds = [ 'g'+c for c in record.TITLES ] + [ 'h'+c for c in record.TITLES ]
    times_writer.writerow(fds)
    gaps_writer.writerow(fds)
    for i in x:
        start = i[0].get_field('A')
        times_writer.writerow(i[0].to_list() + i[1].to_list())
        gaps_writer.writerow(i[0].to_list(start) + i[1].to_list(start))
