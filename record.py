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
    def str_field(self, field):
        """Stringlize a field's value if exists, else -1"""
        if self.fields.__contains__(field):
            return str(self.fields[field])
        else:
            return "{0:5d}.{1:<9d}".format(-1, 0)
    def __str__(self):
        """Stringlize a record"""
        string = "{0:4} {1:10d}+{2:<4d}".format(self.RWBS, self.offset, self.length)
        for field in FIELDS:
            string += ' '
            string += self.str_field(field)
        return string

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
            print(r)

# 按照range来拆分reocrd。
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
        """Split logical offset+length into a list"""
        splitted = []
        max_offset = 0
        for r in self.ranges:
            start = offset - max_offset # possible start in this range if offset is within this range
            max_offset += r.length - 1
            if offset <= max_offset:
                start += r.first
                if r.last - start + 1 >= length:
                    splitted.append([offset, start, length])
                    length = 0
                    return splitted
                else:
                    lth = r.last - start + 1
                    splitted.append([offset, start, lth])
                    offset = max_offset
                    length -= lth
        if length > 0:
            raise ValueError('Ranges couldn\'t map all the blocks')
        return splitted

    def map(self, logic):
        """Find the physic location for logic block"""
        for r in self.ranges:
            if logic < r.length:
                return r.first + logic
            else:
                logic -= r.length
        raise ValueError('Ranges doesn\'t contain logic block {}'.format(logic+1))

    def split(self, table):
        """Split a table"""
        index = 0
        records = []
        for record in table.records:
            splitted = self.split_logic(record.offset, record.length)
            if len(splitted) > 1:
                for piece in splitted:
                    new = record.dup()
                    new.offset = piece[0]
                    new.length = piece[2]
                    records.append([new, piece[1]])
            else:
                records.append([ record, splitted[0][1] ])
            index += 1
        return records
