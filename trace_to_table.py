#!/usr/bin/env python3

# The python version for translating blkparse output into a table. Each row in a table is a record of the time stamps of a request, in this format:
# Offset+Length A(map time) Q(queue time) G(get time) I(insert time) D(driver time) M(merged time) C(complete time)
# A record can't have both M and C time.

import sys

MARK_READ = 1<<0
MARK_WRITE = 1<<1
MARK_COMPLETE = 1<<2
MARK_MERGED = 1<<3
MARK_FINISHED = 1<<4
MARK_FAILED = 1<<5
MARK_UNKNOWN_OP = 1<<6

class field:
    def __init__(self, sec=0, nanosec=0):
        """Initialize a field"""
        self.sec = sec
        self.nanosec = nanosec
    def printf(self, fd=sys.stdout):
        """Print a fields value"""
        print("{0:5d}.{1:<9d}".format(self.sec, self.nanosec), end=' ', file=fd)


class record:
    def __init__(self):
        """Initialize a record"""
        self.offset = 0
        self.length = 0
        self.marks = 0
        self.RWBS = 0
        self.fields = {}
    def print_field(self, field, fd=sys.stdout):
        """Print a field's value if exists, else print -1"""
        if self.fields.__contains__(field):
            self.fields[field].printf(fd)
        else:
            print("{0:5d}.{1:<9d}".format(-1, 0), end=' ', file=fd)
    def printf(self, fd=sys.stdout):
        """Print all fields of a record"""
        print("{0:d}+{1:d}".format(self.offset, self.length), end=' ', file=fd)
        for field in 'A' 'Q' 'G' 'I' 'D' 'M' 'C':
            self.print_field(field, fd)
        print()

class table:
    def __init__(self):
        """Initialize a table"""
        self.records = []

    def find_or_add_record(self, offset, length, RWBS, marks):
        """Find or add record to table"""
        for r in self.records:
            if r.offset == offset and r.marks & marks:
                return r
        else:
            r = record()
            r.offset = offset
            r.length = length
            r.RWBS = RWBS
            r.marks = r.marks | marks
            self.records.append(r)
            return r

    def read_record(self, fd=sys.stdin):
        """Read a record from input, find it in records and update or add a new one"""
        marks = 0
        columns = sys.stdin.readline().split()
        offset = int(columns[0])
        length = int(columns[2])
        RWBS = columns[3]

        if 'R' in RWBS:
            marks = marks | MARK_READ
        elif 'W' in RWBS:
            marks = marks | MARK_WRITE
        else:
            marks = marks | MARK_UNKNOWN_OP
        r = self.find_or_add_record(offset, length, RWBS, marks)

        f = columns[4]
        sec, nanosec = [ int(i) for i in columns[5].split('.') ]
        r.fields[f] = field(sec, nanosec)

t = table()
t.read_record()
for r in t.records:
    r.printf()
