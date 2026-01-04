# csochef
Compression or decompression tool for ISO/CSO 

# CSOChef
Python-based ISO <-> CSO compressor and decompressor for PSP images.  
It allows compressing PlayStation Portable ISO files to CSO format with configurable compression level and alignment, and decompressing CSO back to ISO.

---

## Features

- Compress ISO to CSO (`compress`)  
- Decompress CSO to ISO (`decompress`)  
- Custom compression levels (0–9)  
- Custom block alignment (0–6) for speed/size trade-off  
- Progress bar for both compression and decompression  

---

## Requirements

- Python 3.8+
- `zlib` (standard Python module)
- Works on Windows, Linux, and MacOS

---

## Usage

```bash
# Compress an ISO to CSO
python csochef.py compress input.iso output.cso -l 9 -a 0

# Decompress a CSO to ISO
python csochef.py decompress input.cso output.iso
