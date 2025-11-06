import tempfile
from datetime import datetime

from azul_runner.test_utils import FileManager

from azul_plugin_pdftools.pdfinfo import PDFInfo


def test_pdfinfo():
    """
    Check metadata extraction with pdfinfo python wrapper.
    """
    fm = FileManager()
    # PDF with encrypted owner password rc4.
    f = fm.download_file_bytes("080f79a5c58bc092fc9b99939cb3db35232bb2dd02f2345b0a87e73b0bcf2366")
    with tempfile.NamedTemporaryFile() as fp:
        fp.write(f)
        fp.flush()

        # PDFInfo expects a file path
        p = PDFInfo(fp.name)

    print(p.info)
    assert not p.info["Errors"]
    assert not p.info["Tagged"]
    assert not p.info["Optimized"]
    assert not p.info["JavaScript"]
    assert not p.info["UserProperties"]
    assert not p.info["Encryption Allow Print"]
    assert p.info["Encrypted"]
    assert p.info["Encryption Allow Copy"]
    assert p.info["Encryption Allow Edit"]
    assert p.info["Encryption Allow Add Notes"]
    assert p.info["Encryption Algorithm"] == "RC4"
    assert p.info["Creator"] == "Writer"
    assert p.info["Producer"] == "LibreOffice 4.2"
    # newer releases of popplerutils correctly handle timezone conversion
    assert p.info["CreationDate"] == datetime(2015, 12, 9, 10, 52, 52) or p.info["CreationDate"] == datetime(
        2015, 12, 8, 23, 52, 52
    )
    assert p.info["Pages"] == 1
    assert p.info["Page size"] == "595 x 842 pts (A4)"
    assert p.info["PDF version"] == "1.4"
