#!/usr/bin/env python3

# The python version for translating blkparse output into a table. Each row in a table is a record of the time stamps of a request, in this format:
# Offset+Length A(map time) Q(queue time) G(get time) I(insert time) D(driver time) M(merged time) C(complete time)
# A record can't have both M and C time.
# Arguments:
# i:input o:output O:offset

import sys, argparse
import record

arg_parser = argparse.ArgumentParser(description='Tranlate blkparse output into a table of records.')
arg_parser.add_argument('-i', dest='input', help='Set input file')
arg_parser.add_argument('-o', dest='output', help='Set output file')
arg_parser.add_argument('-O', dest='offset', type=int, default=0, help='Set offset')
args = arg_parser.parse_args()

infile = open(args.input, encoding='utf-8') if args.input else sys.stdin
outfile = open(args.output, encoding='utf-8') if args.output else sys.stdout

t = record.table()
print(args.offset)
t.read_records(infile, int(args.offset))
t.print_table(outfile)
