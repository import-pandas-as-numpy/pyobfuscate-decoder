import base64
import zlib
import ast
from pathlib import Path
import argparse
import os


class ByteStringFinder(ast.NodeVisitor):
    def __init__(self):
        self.results = []

    def visit_Constant(self, node):
        if isinstance(node.value, bytes):
            self.results.append(node.value)

def load_file(file_path: Path) -> str:
    with open(file_path) as f:
        return f.read()
    
def extract_payload(surface_code: str) -> bytes:
    try:
        tree = ast.parse(surface_code)
    except SyntaxError as exc:
        print(f'FATAL {exc}. Input is not valid Python.')
    bsf = ByteStringFinder()
    bsf.visit(tree)
    if len(bsf.results) > 1:
        print('Multiple byte strings found.')
        os.exit()
    elif not bsf.results:
        print('No valid byte strings found in surface file.')
    else:
        return bsf.results[0]

def decode_layer(payload: str) -> str:
    reverse = payload[::-1]
    debase = base64.b64decode(reverse)
    decompress = zlib.decompress(debase)
    return decompress

def _get_payload_indices(marshalled_payload: bytes) -> bytes:
    magic_bytes = b"\x02\x73\x00\x00\x00\x00"
    magic_bytes_end = b"\x4e\x29"
    payload_index_starts = []
    payload_index_ends = []
    for i in range(len(marshalled_payload)):
        substring = marshalled_payload[i:i+len(magic_bytes)]
        if substring[0:1] == magic_bytes[0:1] and substring[-2:] == magic_bytes[-2:]:
            start_index = i+len(magic_bytes)
            payload_index_starts.append(start_index)
    for i in range(len(marshalled_payload)):
        substring = marshalled_payload[i:i+len(magic_bytes_end)]
        if substring == magic_bytes_end:
            payload_index_ends.append(i)
    return payload_index_starts, payload_index_ends

def _try_decode(marshalled_code: bytes, payload_starts: list, payload_ends: list) -> bytes:
    for starts in payload_starts:
        for ends in payload_ends:
            try:
                return decode_layer(marshalled_code[starts:ends])
            except: # Todo: Fix bare except with appropriate exception handling.
                print('Multiple valid substrings detected, trying next payload...')
                pass

def decode_layer_secondary(marshalled_payload: bytes) -> bytes:
    starts, ends =_get_payload_indices(marshalled_payload)
    return _try_decode(marshalled_payload, starts, ends)

def main() -> None:
    parser = argparse.ArgumentParser(
        prog = 'Pyobfuscate Decoder',
        description = 'Attempts to decode PyObfuscate obfuscation.'
    )
    parser.add_argument('filename')
    args = parser.parse_args()
    mal_file = load_file(args.filename)
    extracted_payload = extract_payload(mal_file)
    decoded_layer = decode_layer(extracted_payload)
    while True:
        print(decoded_layer[0:200])
        user_in = input("Is this your code?(Y/N/Q) ")
        if user_in.upper() == 'Y':
            print(decoded_layer)
            break
        elif user_in.upper() == 'N':
            decoded_layer = decode_layer_secondary(decoded_layer)
        else:
            print("Goodbye.")
            break

if __name__ == '__main__':
    main()