from azul_plugin_pdftools.didier import decode_vbe


def test_decode_vbe():
    """
    Test deobfuscating from binary string.
    Note: Decode() function expects 12 byte header/trailer patterns to already be stripped.
    """
    decoded = decode_vbe.Decode(b"#@~^DgAAAA==\\ko$K6,JC\x7fV^GJqAQAAA==^#~@"[12:-12])
    assert decoded == b'MsgBox "Hello"'
