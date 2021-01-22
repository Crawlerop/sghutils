import sghutils
import os
import sys

if len(sys.argv) < 4:
	print(f"Not enough arguments! usage: {sys.argv[0]} input offset output", file=sys.stderr)
	sys.exit(1)

size = os.path.getsize(sys.argv[1])
fd = open(sys.argv[1], "rb")

iTbl = sghutils.ImageTable(fd, int(sys.argv[2], 16))

open(sys.argv[3], "wb").write(iTbl.dump_all())