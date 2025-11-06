import json
import os

from azul_plugin_pdftools.didier import pdfid


def test_pdfid():
    path = os.path.join(os.path.dirname(__file__), "smallpdf.pdf")
    xml = pdfid.PDFiD(path, extraData=True)
    assert xml
    j = pdfid.PDFiD2JSON(xml, False)
    assert j
    d = json.loads(j)["pdfid"]
    # still string values!
    assert d["isPdf"] == "True"
    assert d["countEof"] == "2"
    assert d["countCharsAfterLastEof"] == "0"
    assert d["totalEntropy"] == "7.058126"
    assert d["streamEntropy"] == "7.956656"
    assert d["nonStreamEntropy"] == "4.971046"
    assert d["header"] == "%PDF-1.7"
    # spot check a few of the keyword counts
    assert len(d["keywords"]) == 22
    for k in d["keywords"]:
        if k["name"] in ("obj", "endobj"):
            assert k["count"] == 23
        elif k["name"] in ("stream", "endsteam"):
            assert k["count"] == 2
