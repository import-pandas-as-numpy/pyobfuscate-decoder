# Installation

This decoder operates with no additional dependancies beyond the standard library. As such, installing the script can be as simple as cloning the github repository and invoking the script...
```
git clone https://github.com/import-pandas-as-numpy/pyobfuscate-decoder.git
python pyobfuscate_decoder.py somefile.py
```
In the future, subsequent versions will be made available on PyPI.

# Usage
- This script relies on analysts having the ability to syntactically recognize the obfuscated, marshalled payload from the base marshalled payload.
- Stepping through the successive decoded layers, a glimpse is given at the current decoded layer. If this is still obfuscated, entering `N` for No when prompted will result in another layer of deobfuscation being performed.
- This process will repeat until the desired payload is reached, whereby passing `Y` into the terminal will cause the full marshalled payload to be printed to stdout.
- Passing `Q` will result in the script terminating.

# Internals
- We reference magic bytes found in the payload to determine the start and end point of the obfuscated marshalled payload within successive layers.
- Using these bytes, we extract the string without `marshal.loading` the script to facilitate a fully static analysis.
- After this, the payload is reversed, base64 decoded, and zlib decompressed. The script makes the assumption that successfully zlib decompressing a layer indicates it successfully extracted that layer.
- This layer is subsequently presented (substringed for brevity) for the analyst to determine if the original deobfuscated payload has been reached.

# To Do
- Proper error handling, at the moment we exhaust all possibilities in deobfuscating payloads before exiting less than gracefully.
- Automated base-case detection; the original deobfuscated payloads are visually distinct, but there exist many edge cases that make this detection difficult.
- Packaging and distribution
