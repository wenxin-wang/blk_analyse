#!/usr/bin/env python3

import sys, argparse
import record

ht = record.time.from_str("1392791736.202898100")
gt = record.time.from_str("1392791739.893012929")
print('h-g', ht - gt)
print('g-h', gt - ht)
