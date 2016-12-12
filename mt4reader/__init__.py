# Utility library for loading MT4 HST files
# Based on notes gathered from:
# - http://wejn.org/stuff/mt-hist-info.rb.html
# - http://www.forex-tsd.com/metatrader-4/8116-how-open-hst-file.html#post124232
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import struct
import datetime
import argparse
import sys
import csv


class Bar(object):
    def __init__(self, x):
        if len(x) != 44:
            raise ValueError('Not a full record')
        t, o, l, h, c, v = struct.unpack('<iddddd', x)

        self.time = datetime.datetime.utcfromtimestamp(t)
        self.open = o
        self.low = l
        self.high = h
        self.close = c
        self.volume = v

    def __repr__(self):
        return '%s O:%f L:%f H:%f C:%f' % (self.time, self.open, self.low,
                                           self.high, self.close)

    def __str__(self):
        return '%s O:%f L:%f H:%f C:%f' % (self.time, self.open, self.low,
                                           self.high, self.close)


class History(object):
    def __init__(self, f):
        version, copyright, symbol, period, digits, timesign, lastsync = \
            struct.unpack('<i64s12siiii', f.read(96))
        self.copyright = copyright
        self.symbol = symbol
        self.period = period
        self.digits = digits
        self.timesign = datetime.datetime.utcfromtimestamp(timesign)

        # skip
        f.seek(13*4, 1)
        self.bars = []

        while True:
            x = f.read(44)
            if len(x) != 44:
                break
            self.bars.append(Bar(x))


def convert(in_file, out_file):
    """
    Converts from HST to CSV
    """
    with open(in_file, 'rb') as f:
        history = History(f)

    with open(out_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['time', 'open', 'close', 'high', 'low', 'volume'])
        for b in history.bars:
            writer.writerow([b.time, b.open, b.close, b.high, b.low, b.volume])


def main():
    parser = argparse.ArgumentParser("Convert HST to CSV")
    parser.add_argument('in_file', help="input HST file")
    parser.add_argument('out_file', help="output CSV file")

    args = parser.parse_args()

    convert(args.in_file, args.out_file)

if __name__ == '__main__':
    sys.exit(main())
