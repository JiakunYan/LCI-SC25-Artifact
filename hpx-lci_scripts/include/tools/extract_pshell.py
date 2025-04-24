#!/usr/bin/env python3

import re
import sys

ncores = 128

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} filename".format(sys.argv[0]))
        sys.exit(1)
    filename = sys.argv[1]
    with open(filename, "r") as infile:
        found = False
        for line in infile.readlines():
            m = re.match(r".*PShell.run: (.*)", line)
            if m:
                print(m.groups()[0])
