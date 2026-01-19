# flake8: noqa

__description__ = "Decode VBE script"
__author__ = "Didier Stevens"
__version__ = "0.0.2"
__date__ = "2016/03/29"

"""

Source code put in public domain by Didier Stevens, no Copyright
https://DidierStevens.com
Use at your own risk

History:
  2016/03/28: start
  2016/03/29: 0.0.2 added support for ZIP files and literal arguments with File2StringHash

Todo:

Reference:
  https://gallery.technet.microsoft.com/Encode-and-Decode-a-VB-a480d74c
"""

import binascii
import optparse
import os
import re
import signal
import sys
import textwrap
import zipfile

MALWARE_PASSWORD = b"infected"


def PrintManual():
    manual = """
Manual:

This program reads from the given file or standard input, and converts the encoded VBE script to VBS.

The provided file can be a password protected ZIP file (with password infected) containing the VBE script.

The content of the VBE script can also be passed as a literal argument. This is similar to a Here Document in Unix.
Start the argument (the "filename") with character # to pass a literal argument.
Example: decode-vbe.py "##@~^DgAAAA==\ko$K6,JCV^GJqAQAAA==^#~@"
Result: MsgBox "Hello"

It's also possible to use hexadecimal (prefix #h#) or base64 (prefix #b#) to pass a literal argument.
Example: decode-vbe.py #h#23407E5E4467414141413D3D5C6B6F244B362C4A437F565E474A7141514141413D3D5E237E40
Result: MsgBox "Hello"
Example: decode-vbe.py #b#I0B+XkRnQUFBQT09XGtvJEs2LEpDf1ZeR0pxQVFBQUE9PV4jfkA=
Result: MsgBox "Hello"

"""
    for line in manual.split("\n"):
        print(textwrap.fill(line))


def File2String(filename):
    with open(filename, "rb") as f:
        try:
            return f.read()
        except:
            return None


def File2StringHash(filename):
    decoded = None
    if filename.startswith("#h#"):
        try:
            decoded = binascii.a2b_hex(filename[3:])
        finally:
            return decoded
    elif filename.startswith("#b#"):
        try:
            decoded = binascii.a2b_base64(filename[3:])
        finally:
            return decoded
    elif filename.startswith("#"):
        return filename[1:]
    elif filename.lower().endswith(".zip"):
        oZipfile = zipfile.ZipFile(filename, "r")
        if len(oZipfile.infolist()) == 1:
            oZipContent = oZipfile.open(oZipfile.infolist()[0], "r", MALWARE_PASSWORD)
            data = oZipContent.read()
            oZipContent.close()
        else:
            data = File2String(filename)
        oZipfile.close()
        return data
    else:
        return File2String(filename)


def FixPipe():
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except:
        pass


# Fix for http://bugs.python.org/issue11395
def StdoutWriteChunked(data):
    while data != b"":
        sys.stdout.write(data[0:10000].decode("utf-8"))
        sys.stdout.flush()
        data = data[10000:]


def Decode(data):
    dDecode = {}
    dDecode[9] = b"\x57\x6e\x7b"
    dDecode[10] = b"\x4a\x4c\x41"
    dDecode[11] = b"\x0b\x0b\x0b"
    dDecode[12] = b"\x0c\x0c\x0c"
    dDecode[13] = b"\x4a\x4c\x41"
    dDecode[14] = b"\x0e\x0e\x0e"
    dDecode[15] = b"\x0f\x0f\x0f"
    dDecode[16] = b"\x10\x10\x10"
    dDecode[17] = b"\x11\x11\x11"
    dDecode[18] = b"\x12\x12\x12"
    dDecode[19] = b"\x13\x13\x13"
    dDecode[20] = b"\x14\x14\x14"
    dDecode[21] = b"\x15\x15\x15"
    dDecode[22] = b"\x16\x16\x16"
    dDecode[23] = b"\x17\x17\x17"
    dDecode[24] = b"\x18\x18\x18"
    dDecode[25] = b"\x19\x19\x19"
    dDecode[26] = b"\x1a\x1a\x1a"
    dDecode[27] = b"\x1b\x1b\x1b"
    dDecode[28] = b"\x1c\x1c\x1c"
    dDecode[29] = b"\x1d\x1d\x1d"
    dDecode[30] = b"\x1e\x1e\x1e"
    dDecode[31] = b"\x1f\x1f\x1f"
    dDecode[32] = b"\x2e\x2d\x32"
    dDecode[33] = b"\x47\x75\x30"
    dDecode[34] = b"\x7a\x52\x21"
    dDecode[35] = b"\x56\x60\x29"
    dDecode[36] = b"\x42\x71\x5b"
    dDecode[37] = b"\x6a\x5e\x38"
    dDecode[38] = b"\x2f\x49\x33"
    dDecode[39] = b"\x26\x5c\x3d"
    dDecode[40] = b"\x49\x62\x58"
    dDecode[41] = b"\x41\x7d\x3a"
    dDecode[42] = b"\x34\x29\x35"
    dDecode[43] = b"\x32\x36\x65"
    dDecode[44] = b"\x5b\x20\x39"
    dDecode[45] = b"\x76\x7c\x5c"
    dDecode[46] = b"\x72\x7a\x56"
    dDecode[47] = b"\x43\x7f\x73"
    dDecode[48] = b"\x38\x6b\x66"
    dDecode[49] = b"\x39\x63\x4e"
    dDecode[50] = b"\x70\x33\x45"
    dDecode[51] = b"\x45\x2b\x6b"
    dDecode[52] = b"\x68\x68\x62"
    dDecode[53] = b"\x71\x51\x59"
    dDecode[54] = b"\x4f\x66\x78"
    dDecode[55] = b"\x09\x76\x5e"
    dDecode[56] = b"\x62\x31\x7d"
    dDecode[57] = b"\x44\x64\x4a"
    dDecode[58] = b"\x23\x54\x6d"
    dDecode[59] = b"\x75\x43\x71"
    dDecode[60] = b"\x4a\x4c\x41"
    dDecode[61] = b"\x7e\x3a\x60"
    dDecode[62] = b"\x4a\x4c\x41"
    dDecode[63] = b"\x5e\x7e\x53"
    dDecode[64] = b"\x40\x4c\x40"
    dDecode[65] = b"\x77\x45\x42"
    dDecode[66] = b"\x4a\x2c\x27"
    dDecode[67] = b"\x61\x2a\x48"
    dDecode[68] = b"\x5d\x74\x72"
    dDecode[69] = b"\x22\x27\x75"
    dDecode[70] = b"\x4b\x37\x31"
    dDecode[71] = b"\x6f\x44\x37"
    dDecode[72] = b"\x4e\x79\x4d"
    dDecode[73] = b"\x3b\x59\x52"
    dDecode[74] = b"\x4c\x2f\x22"
    dDecode[75] = b"\x50\x6f\x54"
    dDecode[76] = b"\x67\x26\x6a"
    dDecode[77] = b"\x2a\x72\x47"
    dDecode[78] = b"\x7d\x6a\x64"
    dDecode[79] = b"\x74\x39\x2d"
    dDecode[80] = b"\x54\x7b\x20"
    dDecode[81] = b"\x2b\x3f\x7f"
    dDecode[82] = b"\x2d\x38\x2e"
    dDecode[83] = b"\x2c\x77\x4c"
    dDecode[84] = b"\x30\x67\x5d"
    dDecode[85] = b"\x6e\x53\x7e"
    dDecode[86] = b"\x6b\x47\x6c"
    dDecode[87] = b"\x66\x34\x6f"
    dDecode[88] = b"\x35\x78\x79"
    dDecode[89] = b"\x25\x5d\x74"
    dDecode[90] = b"\x21\x30\x43"
    dDecode[91] = b"\x64\x23\x26"
    dDecode[92] = b"\x4d\x5a\x76"
    dDecode[93] = b"\x52\x5b\x25"
    dDecode[94] = b"\x63\x6c\x24"
    dDecode[95] = b"\x3f\x48\x2b"
    dDecode[96] = b"\x7b\x55\x28"
    dDecode[97] = b"\x78\x70\x23"
    dDecode[98] = b"\x29\x69\x41"
    dDecode[99] = b"\x28\x2e\x34"
    dDecode[100] = b"\x73\x4c\x09"
    dDecode[101] = b"\x59\x21\x2a"
    dDecode[102] = b"\x33\x24\x44"
    dDecode[103] = b"\x7f\x4e\x3f"
    dDecode[104] = b"\x6d\x50\x77"
    dDecode[105] = b"\x55\x09\x3b"
    dDecode[106] = b"\x53\x56\x55"
    dDecode[107] = b"\x7c\x73\x69"
    dDecode[108] = b"\x3a\x35\x61"
    dDecode[109] = b"\x5f\x61\x63"
    dDecode[110] = b"\x65\x4b\x50"
    dDecode[111] = b"\x46\x58\x67"
    dDecode[112] = b"\x58\x3b\x51"
    dDecode[113] = b"\x31\x57\x49"
    dDecode[114] = b"\x69\x22\x4f"
    dDecode[115] = b"\x6c\x6d\x46"
    dDecode[116] = b"\x5a\x4d\x68"
    dDecode[117] = b"\x48\x25\x7c"
    dDecode[118] = b"\x27\x28\x36"
    dDecode[119] = b"\x5c\x46\x70"
    dDecode[120] = b"\x3d\x4a\x6e"
    dDecode[121] = b"\x24\x32\x7a"
    dDecode[122] = b"\x79\x41\x2f"
    dDecode[123] = b"\x37\x3d\x5f"
    dDecode[124] = b"\x60\x5f\x4b"
    dDecode[125] = b"\x51\x4f\x5a"
    dDecode[126] = b"\x20\x42\x2c"
    dDecode[127] = b"\x36\x65\x57"

    dCombination = {}
    dCombination[0] = 0
    dCombination[1] = 1
    dCombination[2] = 2
    dCombination[3] = 0
    dCombination[4] = 1
    dCombination[5] = 2
    dCombination[6] = 1
    dCombination[7] = 2
    dCombination[8] = 2
    dCombination[9] = 1
    dCombination[10] = 2
    dCombination[11] = 1
    dCombination[12] = 0
    dCombination[13] = 2
    dCombination[14] = 1
    dCombination[15] = 2
    dCombination[16] = 0
    dCombination[17] = 2
    dCombination[18] = 1
    dCombination[19] = 2
    dCombination[20] = 0
    dCombination[21] = 0
    dCombination[22] = 1
    dCombination[23] = 2
    dCombination[24] = 2
    dCombination[25] = 1
    dCombination[26] = 0
    dCombination[27] = 2
    dCombination[28] = 1
    dCombination[29] = 2
    dCombination[30] = 2
    dCombination[31] = 1
    dCombination[32] = 0
    dCombination[33] = 0
    dCombination[34] = 2
    dCombination[35] = 1
    dCombination[36] = 2
    dCombination[37] = 1
    dCombination[38] = 2
    dCombination[39] = 0
    dCombination[40] = 2
    dCombination[41] = 0
    dCombination[42] = 0
    dCombination[43] = 1
    dCombination[44] = 2
    dCombination[45] = 0
    dCombination[46] = 2
    dCombination[47] = 1
    dCombination[48] = 0
    dCombination[49] = 2
    dCombination[50] = 1
    dCombination[51] = 2
    dCombination[52] = 0
    dCombination[53] = 0
    dCombination[54] = 1
    dCombination[55] = 2
    dCombination[56] = 2
    dCombination[57] = 0
    dCombination[58] = 0
    dCombination[59] = 1
    dCombination[60] = 2
    dCombination[61] = 0
    dCombination[62] = 2
    dCombination[63] = 1

    result = []
    index = -1
    for byte in (
        data.replace(b"@&", b"\n").replace(b"@#", b"\r").replace(b"@*", b">").replace(b"@!", b"<").replace(b"@$", b"@")
    ):
        if type(byte) == str:
            byte = ord(byte)
        if byte < 128:
            index = index + 1
        if (byte == 9 or byte > 31 and byte < 128) and byte != 60 and byte != 62 and byte != 64:
            byte = dDecode[byte][dCombination[index % 64]]
            if type(byte) == str:
                byte = ord(byte)
        result.append(byte)

    if sys.version_info[0] == 2:
        return str(bytearray(result))
    return bytes(result)


def DecodeVBE(filename, options):
    FixPipe()
    if sys.platform == "win32":
        import msvcrt

        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    if filename == "":
        content = sys.stdin.read()
    else:
        content = File2StringHash(filename)
    oMatch = re.search(b"#@~\\^......==(.+)......==\\^#~@", content)
    if oMatch == None:
        print("No encoded script found!")
    else:
        StdoutWriteChunked(Decode(oMatch.groups()[0]))


def Main():
    oParser = optparse.OptionParser(
        usage="usage: %prog [options] [file]\n" + __description__, version="%prog " + __version__
    )
    oParser.add_option("-m", "--man", action="store_true", default=False, help="Print manual")
    options, args = oParser.parse_args()

    if options.man:
        oParser.print_help()
        PrintManual()
        return

    if len(args) > 1:
        oParser.print_help()
        print("")
        print("  Source code put in the public domain by Didier Stevens, no Copyright")
        print("  Use at your own risk")
        print("  https://DidierStevens.com")
        return
    elif len(args) == 0:
        DecodeVBE("", options)
    else:
        DecodeVBE(args[0], options)


if __name__ == "__main__":
    Main()
