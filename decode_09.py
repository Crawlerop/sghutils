import sghutils
import os
import sys

if len(sys.argv) < 5:
	print(f"Not enough arguments! usage: {sys.argv[0]} input width height output [offset]", file=sys.stderr)
	sys.exit(1)

size = os.path.getsize(sys.argv[1])
fd = open(sys.argv[1], "rb")

img_base_ofs = 0

if len(sys.argv) > 5:
	img_base_ofs = int(sys.argv[5], 16)
	fd.seek(img_base_ofs)

open(sys.argv[4], "wb").write(sghutils.img09_decode(fd, int(sys.argv[2]), int(sys.argv[3]), img_base_ofs))