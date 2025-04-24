#!/usr/bin/env python3

import re
import sys

ncores = 128

if __name__ == "__main__":
    filenames = sys.argv[1:]

    nfiles_not_found = 0
    total_credit = 0
    for filename in filenames:
        filename_pattern = ".*\.n(\d+).*"
        m = re.match(filename_pattern, filename)
        if not m:
            continue
        nnodes = int(m.groups()[0])

        time_pattern = ".*Executed .* configs\. Total time is (\S+)s\."
        with open(filename, "r") as infile:
            found = False
            try:
                for line in infile.readlines():
                    m = re.match(time_pattern, line)
                    if m:
                        time = m.groups()[0]
                        time = float(time)
                        credit = nnodes * ncores * time / 3600
                        found = True
                        print("File: {}: nnodes: {}, time: {}, credit: {}".format(filename, nnodes, time, credit))
                        total_credit += credit
                        break
                if not found:
                    print("{} not found!".format(filename))
                    nfiles_not_found += 1
            except:
                print("Error on file " + filename)
    print("Total files: {}".format(len(filenames)))
    print("Files not found: {}".format(nfiles_not_found))
    print("Total credits: {}".format(total_credit))
