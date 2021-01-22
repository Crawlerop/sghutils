from io import BufferedIOBase, BytesIO, IOBase
import struct

def _img09_decode1(io: IOBase, width: int, height: int, offset: int=0):
    assert io.read(1)[0] == 0x09
    start_bit = io.read(1)[0]
    start_offset = (start_bit*2) + 2
    io.seek(offset+start_offset)

    ret = bytearray()

    while len(ret)<(width*height)*2:
        img09bit = io.read(1)[0]
        
        count = img09bit & 0x3f
        type = img09bit & 0xc0
        
        if type == 0x00:
            for _ in range(count):
                ret += io.read(2)
                
        if type == 0x40:
            for _ in range(count):
                bit_offset = io.read(1)[0]
                data_offset = 2+(bit_offset*2)
                
                old_pos = io.tell()
                io.seek(offset+data_offset)
                
                ret += io.read(2)
                
                io.seek(old_pos)
                
        if type == 0x80:
            ret += io.read(2)*count
            
        if type == 0xc0:
            bit_offset = io.read(1)[0]
            data_offset = 2 + (bit_offset*2)
            
            old_pos = io.tell()
            io.seek(offset+data_offset)
            
            ret += io.read(2)*count
            
            io.seek(old_pos)

    return bytes(ret)


def img09_decode(data: [bytes, bytearray, BufferedIOBase], width: int, height: int, offset: int=0):
    if not isinstance(data, BufferedIOBase):
        data = BytesIO(data)
    return _img09_decode1(data, width, height, offset)

class ImageTable():
    def __init__(self, data: [bytes, bytearray, BufferedIOBase], offset: int=0):
        self._images = []
        self._fd = data
        if not isinstance(data, BufferedIOBase):
            self._fd = BytesIO(self._fd)
        
        self._fd.seek(offset)

        while True:
            width = struct.unpack("<H", self._fd.read(2))[0]
            if width == 0:
                break

            height = struct.unpack("<H", self._fd.read(2))[0]
            offset = struct.unpack("<L", self._fd.read(4))[0]

            orig_pos = self._fd.tell()
            self._fd.seek(offset)

            f_bit = self._fd.read(1)

            imgtmp = {
                "width": width,
                "height": height,
                "offset": offset,
                "type": None,
                "data": None
            }

            if f_bit == b"\x09":
                imgtmp["type"] = "09"

            elif f_bit == b"I" and self._fd.read(3) == b"FEG":
                imgtmp["type"] = "IFGV2"
                
            if imgtmp["type"]:
                self._images.append(imgtmp)

            self._fd.seek(orig_pos)

    def get(self, id: int):
        img = self._images[id]
        if not img["data"]:
            self.hash(id)
        return img["data"]

    def hash_all(self):
        for a in range(len(self._images)):
            self.hash(a)

    def dump_all(self):
        outp = bytearray()
        for a in range(len(self._images)):
            outp += self.get(a)
        return bytes(outp)

    def hash(self, id: int):
        img = self._images[id]
        if img["type"] == "09":
            self._fd.seek(img["offset"])
            img["data"] = bytes(img09_decode(self._fd, img["width"], img["height"], img["offset"]))

        else:
            raise NotImplementedError(f"Image type f{type} is not supported")

if __name__ == "__main__":
    import test_imgs
    print(img09_decode(test_imgs.IMG_09_SAMPLE, 176, 220))
    tbl = ImageTable(test_imgs.IMG_TBL_SAMPLE)

    tbl.hash_all()
    print(tbl.get(0))

    print(tbl.dump_all())