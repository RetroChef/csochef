# CSOChef

Python-based ISO <-> CSO compressor and decompressor for PSP images.  
It allows compressing PlayStation Portable (PSP) ISO files to CSO format with configurable compression level and alignment, and decompressing CSO back to ISO.  
Can be used even by users without Python installed (can be compiled into an executable).  

Works on **Windows, Linux, and MacOS**.

---

## Features
- Compress ISO → CSO  
- Decompress CSO → ISO  
- Optional **SHA-1 verification** to ensure CSO integrity (`--verify`)  
- **Multithreading** support for faster decompression (`-mt`)  
- Adjustable **compression level** (`-l 0-9`)  
- Adjustable **alignment** for CSO padding (`-a 0-6`)  
- Progress bar during compression/decompression  
- Works with most standard CSOs (alignment 0–3 fully supported)  
- Temporary verification ISO automatically cleaned up  

---

## Requirements
- Python 3.10+ (Optional, only if you're running `csochef.py`)  
- `zlib` (standard Python module, only if running `csochef.py`)  

---

## Installation

### Option 1: Use the Windows executable (recommended)
1. Go to the [Releases](https://github.com/RetroChef/csochef/releases) page.  
2. Download `csochef.exe`.  
3. Place it in a folder with your ISO or CSO file.  
4. Run from Command Prompt:
```bash
csochef.exe compress demo.iso demo.cso
csochef.exe decompress demo.cso demo_decompressed.iso
```

### Option 2: Run from Python

1. Make sure Python 3.10 (or higher) is installed.
2. Clone this repository:
```bash
git clone https://github.com/RetroChef/csochef.git
cd csochef
```

### Start compressing/decompressing:

# Compress ISO to CSO
```bash
python csochef.py compress demo.iso demo.cso
```

# Decompress CSO to ISO
```bash
python csochef.py decompress demo.cso demo_decompressed.iso
```

---

## Usage
```bash
python csochef.py <mode> <input> <output> [options]
```

## Arguments
```bash
mode - Choose compress to create a CSO, or decompress to extract an ISO
input - Input file path (ISO for compress, CSO for decompress)
ouput - Output file path (CSO for compress, ISO for decompress)
```

### Options

```bash
-l, --level            Compression level 0–9. 0 = fast/larger, 9 = small/slower
-a, --align            Padding alignment 0–6. Higher numbers = faster but may break some decompressors
--verify               Verify CSO by decompressing and comparing SHA1 hash with original ISO
-mt, --multithread     Enable multithreaded decompression for faster performance
```
### Examples

#### Compress ISO to CSO with default settings:
```bash
csochef.exe compress demo.iso demo.cso
```
#### Compress ISO with alignment 2 and compression level 5
```bash
csochef.exe compress demo.iso demo.cso -a 2 -l 5
```
#### Compress ISO and verify CSO integrity
```bash
csochef.exe compress demo.iso demo.cso --verify
```
#### Decompress CSO to ISO:
```bash
csochef.exe decompress demo.cso demo_decompressed.iso
```
#### Decompress CSO to ISO using multithreading for faster extraction:
```bash
csochef.exe decompress demo.cso demo_decompressed.iso -mt
```
#### Compress ISO with all options (alignment, level, verify)
```bash
csochef.exe compress demo.iso demo.cso -a 1 -l 7 --verify
```
### Notes

Multithreading only applies to decompression, not compression.

CSOs with alignment 4–6 may fail to decompress in some tools, including CSOChef.

Verification will temporarily create a file named __verify_temp__.iso during hash comparison and remove it afterward.

