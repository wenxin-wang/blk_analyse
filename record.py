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

class transaction:
    def __init__(self, offset, length):
        """Initialize transaction"""
        if(length <= 0):
            raise ValueError('Length of a transaction must be larger than 0')
        self.offset = offset
        self.length = length
    def __str__(self):
        """Stringlize transaction"""
        return "{:10d}+{:<4d}".format(self.offset, self.length)
    def contain(self, value):
        """Find if a block is within transaction"""
        return value >= self.offset and value < self.offset + self.length

class field:
    def __init__(self, sec=0, nanosec=0):
        """Initialize a field"""
        self.sec = sec
        self.nanosec = nanosec
    def __str__(self):
        """Stringlize a fields value"""
        return "{0:5d}.{1:<9d}".format(self.sec, self.nanosec)


class record:
    def __init__(self, offset=0, length=0, RWBS='', marks=0):
        """Initialize a record"""
        self.blocks = transaction(offset, length)
        self.marks = marks
        self.RWBS = RWBS
        self.fields = {}
    def dup(self):
        return copy.deepcopy(self)
    def str_field(self, field):
        """Stringlize a field's value if exists, else -1"""
        if self.fields.__contains__(field):
            return str(self.fields[field])
        else:
            return "{0:5d}.{1:<9d}".format(-1, 0)
    def __str__(self):
        """Stringlize a record"""
        string = "{0:4}".format(self.RWBS) + str(self.blocks)
        for field in FIELDS:
            string += ' '
            string += self.str_field(field)
        return string
    def same_offset(self, offset):
        return self.blocks.offset == offset
    def same_length(self, length):
        return self.blocks.length == length

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

        rs = [ r for r in self.records if r.same_offset(offset) and r.marks & marks and not r.marks & MARK_FINISHED ]
        if rs:
            for r in rs:
                if r.same_length(length):
                    return r
            if not r.same_length(length):
                r1 = r.dup()
                r1.blocks.length = length
                self.records.append(r1)
                return r1
        else:
            r = record(offset + global_offset, length, RWBS, marks)
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
            print(r)

class ranges:
    def __init__(self):
        """Initialize transaction"""
        self.ranges = []
    def __str__(self):
        """Stringlize ranges"""
        string = '\n'.join([str(r) for r in self.ranges])
        return string
    def read(self, fd):
        """Read from fd"""
        for line in fd:
            line = line.split('+')
            self.ranges.append(transaction(int(line[0]), int(line[1])))
    def find_range(self, block):
        """Find the transaction a block belongs"""
        for r in self.ranges:
            if r.contain(block):
                return r
        raise ValueError('Ranges doesn\'t contain block {}'.format(block))

    def split_logic(self, offset, length):
        """Split logical t into a list"""
        splitted = []
        o = 0
        i = 0
        for r in self.ranges:
            if o <= offset and o + r.length > offset:
                o = offset - o
                break
            i += 1
            o += r.length
        if not i < len(self.ranges):
            raise ValueError('Ranges couldn\'t map up to logic offset {}' % offset)

        # i is the index of range containing 'offset', o is the offset of 'offset' from the start of that range
        while i < len(self.ranges):
            r = self.ranges[i]
            start = r.offset + o
            if r.length >= length:
                splitted.append([offset, start, length])
                length = 0
                return splitted
            else:
                splitted.append([offset, start, r.length])
                length -= r.length
                offset += r.length
                o = 0
            i += 1
        raise ValueError('Ranges couldn\'t map all the blocks')

    def split(self, table):
        """Split a table"""
        index = 0
        records = []
        for record in table.records:
            splitted = self.split_logic(record.blocks.offset, record.blocks.length)
            if len(splitted) > 1:
                for piece in splitted:
                    new = record.dup()
                    new.blocks.offset = piece[0]
                    new.blocks.length = piece[2]
                    records.append([new, piece[1]])
            else:
                records.append([ record, splitted[0][1] ])
            index += 1
        return records
