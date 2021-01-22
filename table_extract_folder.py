import sghutils
import os
import sys
from PIL import Image

if len(sys.argv) < 4:
	print(f"Not enough arguments! usage: {sys.argv[0]} input offset output [trans]", file=sys.stderr)
	sys.exit(1)

transVal = None

if len(sys.argv) > 4:
	assert len(sys.argv[4]) == 6, "Transparent Color must be atleast 3 bytes (6 hex string length)"
	transVal = []
	transVal.append(bytes.fromhex(sys.argv[4])[0])
	transVal.append(bytes.fromhex(sys.argv[4])[1])
	transVal.append(bytes.fromhex(sys.argv[4])[2])
	transVal = tuple(transVal)

size = os.path.getsize(sys.argv[1])
fd = open(sys.argv[1], "rb")

iTbl = sghutils.ImageTable(fd, int(sys.argv[2], 16))

if not os.path.exists(f"{sys.argv[3]}/"):
	os.mkdir(f"{sys.argv[3]}/")
	
i_path = f"{sys.argv[3]}/"

iTbl.hash_all()

cnt = 1

for img in iTbl._images:
	imTmp = Image.frombytes("RGB", (img["width"], img["height"]), img["data"],"raw", "BGR;16", 0, 1)
	
	if transVal:
		riTmp = imTmp.convert("RGBA").getdata()
		rFin = []

		for ri in riTmp:
			#print(ri[:3], transVal)
			if ri[:3] == transVal:
				rFin.append((255,255,255,0))
			else:
				rFin.append(ri)

		imTmp = imTmp.convert("RGBA")
		imTmp.putdata(rFin)

	imTmp.save(f"{i_path}IMG_{cnt}-c10.png")

	cnt += 1