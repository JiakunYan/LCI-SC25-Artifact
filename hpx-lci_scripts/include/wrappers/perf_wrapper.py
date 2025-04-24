#!/usr/bin/python3
import sys, os
sys.path.append(os.path.join(os.environ["GJS_ROOT_PATH"], "include"))
import pshell

if __name__ == "__main__":
    cmd = "perf record --freq=100 --call-graph dwarf -q " + " ".join(sys.argv[1:])
    cmd = cmd.replace("%%", "$")
    pshell.run(cmd)