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
MARK_MERGER = 1<<4
MARK_FINISHED = 1<<5
MARK_FAILED = 1<<6
MARK_UNKNOWN_OP = 1<<7

class address:
    def __init__(self, offset, length):
        """Initialize address"""
        if(length <= 0):
            raise ValueError('Length of a address must be larger than 0')
        self.offset = offset
        self.length = length
        self.right = offset + length - 1
        self.covered = False
        self.mapped_part = []
    def __str__(self):
        """Stringlize address"""
        return "{:10d}+{:<4d}".format(self.offset, self.length)
    def contain(self, offset):
        """Find if a offset is within address"""
        return offset >= self.offset and offset <= self.right
    def overlap(self, addr):
        """Find if it overlap an addr"""
        if self.offset <= addr.offset:
            return self.contain(addr.offset) or addr.contain(self.right)
        else:
            return self.contain(addr.right) or addr.contain(self.offset)
    def map(self, offset, length):
        if self.covered:
            raise ValueError("Address already covered")
        if not self.contain(offset) or not self.contain(offset+length-1):
            raise ValueError("Address can't map {}+{}".format(offset, length))
        addr = address(offset, length)
        if self.mapped(addr):
            raise ValueError("Address already mapped {}+{}".format(offset, length))
        self.mapped_part.append(addr)
        l = 0
        for a in self.mapped_part:
            l += a.length
        if l >= self.length:
            self.covered = True
    def mapped(self, addr):
        for piece in self.mapped_part:
            if piece.overlap(addr):
                return True
    def mapped_offset(self, offset):
        for piece in self.mapped_part:
            if piece.contain(offset):
                return True

class time:
    def __init__(self, sec=0, nanosec=0):
        """Initialize a time"""
        self.sec = sec
        self.nanosec = nanosec
    def __str__(self):
        """Stringlize a times value"""
        return "{0:5d}.{1:<9d}".format(self.sec, self.nanosec)
    def __sub__(self, t):
        """time __sub__ time"""
        nanosec = self.nanosec - t.nanosec
        sec = self.sec - t.sec
        if nanosec < 0:
            if sec<=0:
                nanosec = -nanosec
            else:
                nanosec += 10**9
                sec -= 1
        elif nanosec > 0:
            if sec<0:
                nanosec = 10**9 - nanosec
                sec += 1
        return time(sec, nanosec)
    def __add__(self, t):
        """time __add__ time"""
        nanosec = self.nanosec + t.nanosec
        sec = nanosec // 10**9
        nanosec %= 10**9
        sec += (self.sec + t.sec)
        return time(sec, nanosec)

    @classmethod
    def from_str(cls, string):
        """Construct time from string"""
        sec, nanosec = [ int(i) for i in string.split('.') ]
        return cls(sec, nanosec)

class record:
    def __init__(self, offset=0, length=0, RWBS='', marks=0):
        """Initialize a record"""
        self.blocks = address(offset, length)
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

        rs = [ r for r in self.unfinished if r.same_offset(offset) and r.marks & marks ]
        #print(marks, len(self.unfinished), len(self.records), len(rs))
        if rs:
            for r in rs:
                if r.same_length(length):
                    return r
                else:
                    r.marks |= (MARK_MERGER | MARK_FINISHED)
                    self.unfinished.remove(r)
                    self.records.append(r)

            if not r.same_length(length):
                r1 = r.dup()
                r1.blocks.length = length
                self.unfinished.append(r1)
                return r1
        else:
            r = record(offset + global_offset, length, RWBS, marks)
            self.unfinished.append(r)
            return r

    def read_records(self, fd=sys.stdin, global_offset=0, time_offset=time(0,0)):
        """Read records from fd"""
        self.unfinished = []
        for line in fd:
            self.read_record(line, global_offset, time_offset)
        for r in self.unfinished:
            self.records.append(r)
        del self.unfinished

    def read_record(self, line, global_offset, time_offset):
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

        t = time.from_str(columns[5])
        t = t + time_offset
        r.fields[f] = t # if f exists, we overwrite it

        if f[0] in FINAL_ACTIONS:
            self.unfinished.remove(r)
            r.marks |= MARK_FINISHED
            self.records.append(r)

    def print_table(self, fd=sys.stdout):
        """Print the table"""
        print("{:4}  {}  {:16}{:16}{:16}{:16}{:16}{:16}{}".format("RWBS", "Offset and Length", 'A', 'Q', 'G', 'I', 'D', 'M', 'C'), file=fd)
        for r in self.records:
            print(r)

    def filter(self, ranges):
        self.records = [ r for r in self.records if ranges.find_block(r.blocks.offset) ]

class r2a_maps:
    def __init__(self):
        """Initialize r2a_maps"""
        self.maps = []
    def add(self, record, address):
        """Add a r2a_map"""
        self.maps.append([record, address])
    def print_maps(self):
        """Print r2a_maps"""
        for m in self.maps:
            for o in m:
                print(o)
    def split_grecord(self, offset, length, htable):
        """Split a guest record"""
        a2r = []
        to_del = []
        for hr in htable.records:
            if hr.blocks.covered:
                to_del.append(hr)
            if length <= 0:
                break
            if hr.blocks.contain(offset):
                if hr.blocks.mapped_offset(offset):
                    print('fuck', offset)
                    continue
                lth = hr.blocks.length - (offset - hr.blocks.offset)
                if  lth >= length:
                    hr.blocks.map(offset, length)
                    a2r.append([offset, length, hr])
                    break
                else:
                    hr.blocks.map(offset, lth)
                    a2r.append([offset, lth, hr])
                    offset += lth
                    length -= lth
        for hr in to_del:
            htable.records.remove(hr)
        if len(a2r) == 0:
            raise ValueError('Htable couldn\'t map up to logic offset {}'.format(offset))
        return a2r

    def gen_r2r_maps(self, htable):
        """Generate r2r_maps from host table"""
        r2r_maps = []
        for m in self.maps:
            record = m[0]
            addr = m[1]
            try:
                a2r = self.split_grecord(addr.offset, addr.length, htable)
            except ValueError as e:
                print(record, addr)
                print(e)
                continue
            if len(a2r) > 1:
                for piece in a2r:
                    new = record.dup()
                    new.blocks.offset = record.blocks.offset + piece[0] - addr.offset
                    new.blocks.length = piece[1]
                    r2r_maps.append([new, piece[2]])
            else:
                r2r_maps.append([record, a2r[0][2]])
        return r2r_maps

class ranges:
    def __init__(self):
        """Initialize address"""
        self.ranges = []
    def __str__(self):
        """Stringlize ranges"""
        string = '\n'.join([str(r) for r in self.ranges])
        return string
    def read(self, fd):
        """Read from fd"""
        for line in fd:
            line = line.split('+')
            self.ranges.append(address(int(line[0]), int(line[1])))
    def find_block(self, block):
        """Find the address a block belongs"""
        for r in self.ranges:
            if r.contain(block):
                return r
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
            lth = r.length - o
            if lth >= length:
                splitted.append([offset, start, length])
                length = 0
                return splitted
            else:
                splitted.append([offset, start, lth])
                length -= lth
                offset += lth
                o = 0
            i += 1
        raise ValueError('Ranges couldn\'t map all the blocks')

    def split(self, table):
        """Split a table"""
        ramaps = r2a_maps()
        for record in table.records:
            splitted = self.split_logic(record.blocks.offset, record.blocks.length)
            if len(splitted) > 1:
                for piece in splitted:
                    new = record.dup()
                    new.blocks.offset = piece[0]
                    new.blocks.length = piece[2]
                    ramaps.add(new, address(piece[1], piece[2]))
            else:
                ramaps.add(record, address(splitted[0][1], splitted[0][2]))
        return ramaps
