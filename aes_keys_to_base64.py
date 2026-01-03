r"""
Convert the aes_keys output from Volatility's bulk_extractor.exe into Base64-encoded strings, removing duplicates. 

How you get here: 
    FTK Imager > Capture Memory
    Run bulk_extractor on the memdump.mem file enabling *only* aes, producing aes_keys.txt in the form:

    | # BANNER FILE NOT PROVIDED (-b option)
    | # BULK_EXTRACTOR-REC-Version: 1.6.0-dev-rec03 ($Rev: 10844 $)
    | # Feature-Recorder: aes_keys
    | # Filename: C:\Users\Axel\Desktop\memdump.mem
    | # Feature-File-Version: 1.1
    | 62596544  6d 53 83 e8 ee 92 5b ba 4e 08 bc e4 7e aa 37 b2 ff d6 c2 4b f5 d9 fa 75 e9 c9 1d a3 54 46 b3 df     AES256
    | 62597216  6d 53 83 e8 ee 92 5b ba 4e 08 bc e4 7e aa 37 b2 ff d6 c2 4b f5 d9 fa 75 e9 c9 1d a3 54 46 b3 df     AES256
    | 62597888  6d 53 83 e8 ee 92 5b ba 4e 08 bc e4 7e aa 37 b2 ff d6 c2 4b f5 d9 fa 75 e9 c9 1d a3 54 46 b3 df     AES256
    | 4470813360    c0 35 15 c2 05 7e 60 7d 39 f7 a2 99 1e 44 16 85     AES128
    | 4471081904    53 25 fa a7 6d 6c bd b1 75 fd 3b d4 1d 96 b8 6a 1c 6f 2e 10 62 d9 40 a6 d4 2f 03 3b f0 f5 30 ca     AES256

Challenge reference: pc2/round3a-100-buckets

"""
import sys
from pathlib import Path
import logging
from collections import namedtuple
from typing import Iterable
import binascii
import base64


Key = namedtuple('Key', ['offset', 'hexbytes', 'keytype'])


def main(infile: str):
    inpath = Path(infile)
    with open(inpath, 'r') as f:
        raw = f.read().strip()
    data = convert_raw_string_to_data(raw)
    hex_keys = [x.hexbytes for x in data]
    freqs = convert_list_of_hexbytes_with_freq(hex_keys)
    logging.info("Reduced to %d keys", len(freqs))
    logging.info("Printing each Base64 key along with the number of times it was seen")
    for key, count in sorted(freqs.items(), key=lambda item: item[1], reverse=True):
        print(count, '\t', key)
    return


def convert_raw_string_to_data(raw: str) -> Iterable[Key]:
    """Place offset, hex bytes, and key type into structured data."""
    raw_lines = raw.split('\n')
    lines = [x.strip() for x in raw_lines if not x.startswith('#')]

    data = []
    for line in lines:
        try:
            offset, hexbytes, key = line.split('\t')
        except ValueError:
            logging.error("Could not split into three elements: %s", line)
        else:
            k = Key(offset, hexbytes, key)
        data.append(k)
    logging.info("Found %d tuples", len(data))
    return data


def get_unique_hex_values(data: Iterable[Key]) -> list:
    """De-duplicate hex bytes from a list of Key tuples."""
    hexbytes = [x.hexbytes for x in data]
    deduped_hexbytes = set(hexbytes)
    return list(deduped_hexbytes)


def convert_list_of_hexbytes_with_freq(hex_keys: list) -> dict:
    """Convert each hexbytes key to its base64 string, keeping track of how many times it was seen."""
    freqs = {}
    for key in hex_keys:
        b64 = hex_to_base64(key)
        if b64 in freqs.keys():
            freqs[b64] += 1
        else:
            freqs[b64] = 1
    return freqs


def hex_to_base64(s: str) -> str:
    """Convert and encode a single hex to get Base64 string as ascii."""
    s = s.replace(' ', '')
    byte_data = binascii.unhexlify(s)
    b64_string = base64.b64encode(byte_data).decode('ascii')
    return b64_string


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    main(sys.argv[1])

