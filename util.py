import codecs
from datetime import datetime
from mongodb import create_bson_decimal


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


def to_decimal(trs, key, is_german):
    if is_german:
        trs[key] = create_bson_decimal(trs[key].replace(".", "").replace(",", "."))
    else:
        trs[key] = create_bson_decimal(trs[key])
    return trs[key]


def to_int(trs, key):
    trs[key] = int(trs[key])


def rename_key(trs, src, dst):
    trs[dst] = trs[src]
    del trs[src]