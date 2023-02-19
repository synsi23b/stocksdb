import codecs
from datetime import datetime


def convert_to_utf8(src, dst, source_encoding="cp1252"):
    BLOCKSIZE = 1048576  # or some other, desired size in bytes
    with codecs.open(src, "r", source_encoding) as sourceFile:
        with codecs.open(dst, "w", "utf-8") as targetFile:
            while True:
                contents = sourceFile.read(BLOCKSIZE)
                if not contents:
                    break
                targetFile.write(contents)


def to_dt(trs, key, pattern):
    trs[key] = datetime.strptime(trs[key], pattern)


def to_float(trs, key):
    trs[key] = float(trs[key].replace(",", "."))


def to_int(trs, key):
    trs[key] = int(trs[key])


def rename_key(trs, src, dst):
    trs[dst] = trs[src]
    del trs[src]


def _to_int(a, b):
    a, b = str(a), str(b)
    adec, bdec = a.find("."), b.find(".")
    adec = len(a) - adec
    bdec = len(b) - bdec
    a, b = a.replace(".", ""), b.replace(".", "")
    if adec > bdec:
        decs = adec - 1
        b += "0" * (adec - bdec)
    else:
        decs = bdec - 1
        a += "0" * (bdec - adec)
    return int(a), int(b), decs


def _to_float(res, decs):
    res = str(res)
    res = res[:-decs] + "." + res[-decs:]
    return float(res)


def integer_plus(a, b):
    a, b, decs = _to_int(a, b)
    return _to_float(a+b, decs)


def integer_minus(a, b):
    a, b, decs = _to_int(a, b)
    return _to_float(a-b, decs)


if __name__ == "__main__":
    print(integer_plus(45.432, 101.0))