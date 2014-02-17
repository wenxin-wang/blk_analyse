import sys, copy

# record.py定义了record。record是每个读／写请求从发起到完成的记录，将各个动作发生的时间点记录下来。
# Offset+Length A(map time) Q(queue time) G(get time) I(insert time) D(driver time) M(merged time) C(complete time)
# A record can't have both M and C time.

FIELDS = "AQGIDMC"
FINAL_ACTIONS = "MC"

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
    def __str__(self):
        """Stringlize a fields value"""
        return "{0:5d}.{1:<9d}".format(self.sec, self.nanosec)


class record:
    def __init__(self):
        """Initialize a record"""
        self.offset = 0
        self.length = 0
        self.marks = 0
        self.RWBS = ''
        self.fields = {}
    def dup(self):
        return copy.deepcopy(self)
    def print_field(self, field, fd=sys.stdout):
        """Print a field's value if exists, else print -1"""
        if self.fields.__contains__(field):
            print(self.fields[field], end=' ', file=fd)
        else:
            print("{0:5d}.{1:<9d}".format(-1, 0), end=' ', file=fd)
    def print_record(self, fd=sys.stdout):
        """Print all fields of a record"""
        print("{0:4} {1:10d}+{2:<4d}".format(self.RWBS, self.offset, self.length), end=' ', file=fd)
        for field in FIELDS:
            self.print_field(field, fd)
        print()

class table:
    def __init__(self):
        """Initialize a table"""
        self.records = []

    def find_or_add_record(self, offset, length, RWBS, global_offset):
        """Find or add record to table"""
        marks = 0
        if 'R' in RWBS:
            marks |=  MARK_READ
        elif 'W' in RWBS:
            marks |= MARK_WRITE
        else:
            marks |= MARK_UNKNOWN_OP

        rs = [ r for r in self.records if r.offset == offset and r.marks & marks and not r.marks & MARK_FINISHED ]
        if rs:
            for r in rs:
                if r.length == length:
                    return r
            if r.length != length:
                r1 = r.dup()
                r1.length = length
                self.records.append(r1)
                return r1
        else:
            r = record()
            r.offset = offset + global_offset
            r.length = length
            r.RWBS = RWBS
            r.marks = r.marks | marks
            self.records.append(r)
            return r

    def read_records(self, fd=sys.stdin, global_offset=0):
        """Read records from fd"""
        for line in fd:
            self.read_record(line, global_offset)

    def read_record(self, line, global_offset):
        """Read a record from input, find it in records and update or add a new one"""
        marks = 0
        columns = line.split()
        offset = int(columns[0])
        length = int(columns[2])
        RWBS = columns[3]
        f = columns[4]
        if f[0] not in FIELDS:
            return None

        r = self.find_or_add_record(offset, length, RWBS, global_offset)

        sec, nanosec = [ int(i) for i in columns[5].split('.') ]
        r.fields[f] = field(sec, nanosec) # if f exists, we overwrite it

        if f[0] in FINAL_ACTIONS:
            r.marks |= MARK_FINISHED

    def print_table(self, fd=sys.stdout):
        """Print the table"""
        print("{:4}  {}  {:16}{:16}{:16}{:16}{:16}{:16}{}".format("RWBS", "Offset and Length", 'A', 'Q', 'G', 'I', 'D', 'M', 'C'), file=fd)
        for r in self.records:
            r.print_record()
