#!/usr/bin/python3
from Tree import *
from Shell import *

import io
import sys

if len(sys.argv) < 2:
    raise ValueError('Script requires single argument')

tree = Tree()
shell = Shell(tree)

with open(sys.argv[1]) as script:
    for line in script.readlines():
        line = line.strip()
        if line.startswith('#'):
            print(line)
            continue

        print("COMMAND:", line)
        command = shell.parse(line)
        if command == None:
            print("WARNING: No parse output for: '{}'".format(line))
            continue

        result = tree.execute(command)
        if result != None:
            Shell.pretty_print(result)

