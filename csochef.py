import zlib
import struct
import os
import sys
import argparse
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

def sha1_file(path, chunk_size = 1024 * 1024):
    sha1 = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha1.update(chunk)

    return sha1.hexdigest()

BLOCK_SIZE = 2048
CISO_MAGIC = 0x4F534943  # 'CISO' as integer
HEADER_SIZE = 0x18

# Progress bar
def update_progress(current, total, bar_length=40):
    
    if total == 0:
        return
    progress = current / total


    block = int(bar_length * progress)
    update = (
        f"\rProgress: [{'#' * block}{'-' * (bar_length - block)}] {progress*100:5.1f}%"
    )

   
    sys.stdout.write(update)
    sys.stdout.flush()

# Compressor (ISO to CSO)

def iso2cso(iso_path, cso_path, level=9, align=0, multithread=False):
    """
    Compress an ISO to CSO format with optional alignment.
    align: 0=small/slow, 6=fast/large
    """
    align_bytes = 1 << align      # Alignment size: 2^align bytes
    align_mask = align_bytes - 1  # Used to detect misalignment

    iso_size = os.path.getsize(iso_path)
    total_blocks = (iso_size + BLOCK_SIZE - 1) // BLOCK_SIZE

    offsets = []
    current_offset = HEADER_SIZE + (total_blocks + 1) * 4  # Start of first block

    with open(iso_path, "rb") as iso, open(cso_path, "wb") as cso:
        # Write placeholder header + offset table
        cso.write(b"\x00" * HEADER_SIZE)
        cso.write(b"\x00" * ((total_blocks + 1) * 4))

        for block in range(total_blocks):
            data = iso.read(BLOCK_SIZE)

            # Strip the first 2 bytes to get raw DEFLATE stream for PSP CSO
            compressed = zlib.compress(data, level)[2:]

            # Apply alignment padding if needed
            pad = current_offset & align_mask
            if pad:
                padding = align_bytes - pad
                cso.write(b"\x00" * padding)
                current_offset += padding

            # Store offset and write data
            if len(compressed) < len(data):
                offsets.append(current_offset >> align)
                cso.write(compressed)
                current_offset += len(compressed)
            else:
                offsets.append((current_offset >> align) | 0x80000000)
                cso.write(data)
                current_offset += len(data)

            update_progress(block + 1, total_blocks)

        print()     #\n newline

        # Final offset (end of last sector)
        offsets.append(current_offset >> align)

        # Write CSO header
        cso.seek(0)
        header = struct.pack(
            "<LLQLBBxx",
            CISO_MAGIC,
            HEADER_SIZE,
            iso_size,
            BLOCK_SIZE,
            1,        # Version
            align
        )
        cso.write(header)

        # Write offset table
        for off in offsets:
            cso.write(struct.pack("<I", off))

    print("Done Compressing!")
    print(f"ISO SIZE: {iso_size} bytes")
    print(f"CSO SIZE: {os.path.getsize(cso_path)} bytes")

def decompress_blocks(args):
    index, offsets, cso_path, block_size, align = args

    with open(cso_path, "rb") as fin:
        current = offsets[index]
        next_off = offsets[index + 1]

        is_raw = current & 0x80000000
        current &= 0x7FFFFFFF
        next_off &= 0x7FFFFFFF

        start = current << align
        end = next_off << align


        fin.seek(start)
        data = fin.read(end - start)

        if is_raw:
            block = data
        else:
            block = zlib.decompress(data, wbits=-15)

        return index, block[:block_size]


# Decompressor (CSO to ISO)
def cso2iso(cso_path, iso_path, multithread=False):
    with open(cso_path, "rb") as fin, open(iso_path, "wb") as fout:
        header = fin.read(HEADER_SIZE)
        magic, header_size, iso_size, block_size, version, align = struct.unpack("<LLQLBBxx", header)

        if magic != CISO_MAGIC:
            raise ValueError("Not a Valid CSO File")

        print("CSO Header:")
        print(" ISO size:", iso_size)
        print(" Block size:", block_size)
        print(" Align:", align)

        total_blocks = (iso_size + block_size - 1) // block_size
        offsets = [struct.unpack('<I', fin.read(4))[0] for _ in range(total_blocks + 1)]

        if multithread:
            print("Multithreading Enabled")

            results = [None] * total_blocks

            work = [
                (i, offsets, cso_path, block_size, align)
                for i in range(total_blocks)
                    
                    ]
            
            with ThreadPoolExecutor() as executor:
                completed = 0
                for future in as_completed(
                    executor.submit(decompress_blocks, w) for w in work
                ):
                    i, block = future.result()
                    results[i] = block
                    completed += 1
                    update_progress(completed, total_blocks)
            
            for block in results:
                fout.write(block)

        else:
            for i in range(total_blocks):
                index, block = decompress_blocks(
                    (i, offsets, cso_path, block_size, align)
                )

                fout.write(block)
                update_progress(i + 1, total_blocks)

        print()
    print("Done Decompressing!")
    print(f"ISO SIZE: {iso_size} bytes")


def verify_cso(original_iso, cso_path):
    print("Verifying CSO Integrity...")

    temp_iso = "__verify_temp__.iso"

    try:
        #Decompress CSO to temp ISO
        cso2iso(cso_path, temp_iso, multithread=False)

        #Compute hash
        original_hash = sha1_file(original_iso)
        decompressed_hash = sha1_file(temp_iso)

        print("Original ISO SHA1: ", original_hash)
        print("Decompressed ISO SHA1: ", decompressed_hash)

        if original_hash == decompressed_hash:
            print("Verification Passed: CSO is Valid")

        else:

            print("Verification Failed: Data Mismatch")

    finally:
        if os.path.exists(temp_iso):
            os.remove(temp_iso)

# Main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSO Compressor & Decompressor by RetroChef")
    parser.add_argument("mode", choices=["compress", "decompress"], help="Choose mode: compress ISO->CSO or decompress CSO->ISO")
    parser.add_argument("input", help="Input file (ISO or CSO)")
    parser.add_argument("output", help="Output file (CSO or ISO)")
    parser.add_argument("-l", "--level", type=int, default=9, choices=range(0, 10), help="Compression level 1-9 (1=fast/large, 9=small/slow), Default is 9")
    parser.add_argument("-a", "--align", type=int, default=0, choices=range(0, 7), help="Padding alignment 0=small/slow, 6=fast/large, Default is 0")
    parser.add_argument("--verify", action="store_true", help="Verify CSO by decompressing and comparing hashes")
    parser.add_argument("-mt", "--multithread", action="store_true", help="Enables multithreading for faster compression/decompression" ) 
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: {args.input} does not exist.")
        sys.exit(1)
    if args.mode == "compress" and args.multithread:
        print("Warning: Multithreading only applies to decompression")
    if args.mode == "compress":
        iso2cso(args.input, args.output, level=args.level, align=args.align, multithread=args.multithread)

        if args.verify:
            verify_cso(args.input, args.output)
    else:
        cso2iso(args.input, args.output, args.multithread)
