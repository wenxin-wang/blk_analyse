# g_to_h.py将guest上的record映射到host上的record。如果需要，对guest上的record进行必要的拆分。

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
        """Split offset+length into a list"""
        list = []
        for r in self.ranges:
            if offset < r.length:
                left = r.first + offset
                if r.last - left + 1 >= length:
                    list.append([left, length, str(r)])
                    length = 0
                    return list
                else:
                    lth = r.last - left + 1
                    list.append([left, lth, str(r)])
                    offset = 0
                    length -= lth
            else:
                offset -= r.length
        if length > 0:
            raise ValueError('Ranges couldn\'t map all the blocks')
        return list

    def map(self, logic):
        """Find the physic location for logic block"""
        for r in self.ranges:
            if logic < r.length:
                return r.first + logic
            else:
                logic -= r.length
        raise ValueError('Ranges doesn\'t contain logic block {}'.format(logic+1))
