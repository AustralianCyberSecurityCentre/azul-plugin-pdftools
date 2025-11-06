"""Analyse PDF's using Didier Stevens' PDFiD script."""

import json
from tempfile import NamedTemporaryFile

from azul_runner import (
    BinaryPlugin,
    Feature,
    FeatureValue,
    Job,
    State,
    add_settings,
    cmdline_run,
)

from .didier import pdfid


class AzulPluginPdfId(BinaryPlugin):
    """Analyse PDF's using Didier Stevens' PDFiD script."""

    CONTACT = "ASD's ACSC"
    VERSION = "2025.03.19"
    SETTINGS = add_settings(
        filter_data_types={"content": ["document/pdf", "document/pdf/"]},
    )
    FEATURES = [
        Feature(name="pdf_version", desc="PDF version header", type=str),
        Feature(name="pdf_keyword_count", desc="Number of times the labelled keyword appears in document", type=int),
        Feature(name="pdf_keyword_hex_count", desc="Count of keyword with hex encoding in document", type=int),
        Feature(name="pdf_date_field", desc="Timestamp field appearing in document", type=str),  # unparsed values
        Feature(name="pdf_entropy_stream", desc="Entropy across stream data", type=float),
        Feature(name="pdf_entropy_nonstream", desc="Entropy across contents outside of streams", type=float),
        Feature(name="pdf_entropy_total", desc="Entropy across entire document contents", type=float),
        Feature(name="pdf_trailing_bytes", desc="Count of bytes after last PDF %%EOF marker", type=int),
        Feature(name="pdf_eof_count", desc="Count of PDF %%EOF markers", type=int),
        Feature(name="tag", desc="Any information label about the document", type=str),
    ]

    @staticmethod
    def can_convert_to_float(val: str):
        """Check if a value can be cast to a float."""
        try:
            float(val)
            return True
        except ValueError:
            return False

    def execute(self, job: Job):
        """Process any PDF Documents and extract high-level features."""
        features = {}
        # only takes filepath as input not buffer
        with NamedTemporaryFile(delete=True) as tmp:
            tmp.write(job.get_data().read())
            tmp.flush()
            xml_doc = pdfid.PDFiD(tmp.name, extraData=True)
            # unable to parse as a pdf
            if not xml_doc.documentElement.getAttribute("IsPDF") == "True":
                return State.Label.OPT_OUT

        meta = json.loads(pdfid.PDFiD2JSON(xml_doc, force=False))
        meta = meta.get("pdfid")

        if meta.get("header"):
            features["pdf_version"] = meta["header"]
        if meta.get("countEof"):
            features["pdf_eof_count"] = int(meta["countEof"])
        if meta.get("countCharsAfterLastEof"):
            # unlike other fields, don't set if no value
            count = int(meta["countCharsAfterLastEof"])
            if count:
                features["pdf_trailing_bytes"] = count
        if meta.get("streamEntropy"):
            if self.can_convert_to_float(meta["streamEntropy"]):
                features["pdf_entropy_stream"] = float(meta["streamEntropy"])
        if meta.get("nonStreamEntropy"):
            if self.can_convert_to_float(meta["nonStreamEntropy"]):
                features["pdf_entropy_nonstream"] = float(meta["nonStreamEntropy"])
        if meta.get("totalEntropy"):
            if self.can_convert_to_float(meta["totalEntropy"]):
                features["pdf_entropy_total"] = float(meta["totalEntropy"])

        # just feature the raw date strings
        # other plugins will do parsed versions if they're parseable
        for d in meta.get("dates"):
            features.setdefault("pdf_date_field", []).append(FeatureValue(d["value"], label=d["name"]))

        for k in meta.get("keywords"):
            # only store if the keyword was seen
            if not k.get("count"):
                continue

            # count of keyword in doc
            features.setdefault("pdf_keyword_count", []).append(FeatureValue(int(k["count"]), label=k["name"]))

            # hex escaping in keyword.
            if k.get("hexcodecount"):
                features.setdefault("pdf_keyword_hex_count", []).append(
                    FeatureValue(int(k["hexcodecount"]), label=k["name"])
                )

            # flag encrypted docs for interest
            if k.get("name") == "/Encrypt":
                features["tag"] = "encrypted_pdf"

        self.add_many_feature_values(features)


def main():
    """Run plugin via command-line."""
    cmdline_run(plugin=AzulPluginPdfId)


if __name__ == "__main__":
    main()
