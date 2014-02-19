#!/usr/bin/env python3

import sys
from record import address

a1 = address(0,1)
a2 = address(0,1)
print(a1.overlap(a2))
print(a2.overlap(a1))

a1 = address(0,1)
a2 = address(1,1)
print(a1.overlap(a2))
print(a2.overlap(a1))

a1 = address(0,3)
a2 = address(2,1)
print(a1.overlap(a2))
print(a2.overlap(a1))

a1 = address(0,3)
a1.map(2, 1)
for m in a1.mapped_part:
    print(m)
a1.map(1, 1)
for m in a1.mapped_part:
    print(m)
a1.map(0, 1)
for m in a1.mapped_part:
    print(m)
a1.map(0, 1)
