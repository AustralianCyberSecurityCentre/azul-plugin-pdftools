"""Analyse PDF's using the pdfminer python library.

Extract any printable text within a PDF document and raise it
as a text stream for display and search indexing.
Any URI objects in the document are also extracted and raised as network features.
"""

from contextlib import closing
from io import StringIO

from azul_runner import (
    BinaryPlugin,
    Feature,
    FeatureType,
    Job,
    add_settings,
    cmdline_run,
)
from pdfminer import psexceptions
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument, PDFPasswordIncorrect, PDFSyntaxError
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import PDFStream
from pydantic import TypeAdapter, ValidationError
from pydantic.networks import HttpUrl

httpUrlValidator = TypeAdapter(HttpUrl)


class AzulPluginPdfText(BinaryPlugin):
    """Analyse PDF's using the pdfminer python library."""

    CONTACT = "ASD's ACSC"
    VERSION = "2025.03.19"
    SETTINGS = add_settings(
        max_page_count=(int, 100),
        filter_data_types={"content": ["document/pdf", "document/pdf/"]},
    )
    FEATURES = [
        Feature(name="pdf_embedded_uri", desc="URI link embedded in the PDF document", type=FeatureType.Uri),
        Feature(
            name="pdf_embedded_non_http_uri",
            desc="Non-HTTP URI link embedded in the PDF document",
            type=FeatureType.String,
        ),
        Feature(name="tag", desc="Any information label about the document", type=FeatureType.String),
    ]

    def execute(self, job: Job):
        """Extract text and URI objects from a PDF document using pdfminer."""
        try:
            parser = PDFParser(job.get_data())
            doc = PDFDocument(parser)
        except PDFPasswordIncorrect:
            self.add_feature_values("tag", "encrypted_pdf")
            return
        except (ValueError, psexceptions.PSEOF):
            return self.is_malformed("Malformed PDF that failed parsing.")
        except PDFSyntaxError as ex:
            raise ex

        outfp = StringIO()
        rscrmgr = PDFResourceManager(caching=True)
        laparams = LAParams()
        with closing(TextConverter(rscrmgr, outfp, laparams=laparams)) as device:
            interpreter = PDFPageInterpreter(rscrmgr, device)
            for i, page in enumerate(PDFPage.create_pages(doc)):
                interpreter.process_page(page)
                if i >= self.cfg.max_page_count:
                    break

        urls = set()
        # walk the tree of xrefs looking for URI objects
        for xref in doc.xrefs:
            for objid in xref.get_objids():
                try:
                    obj = doc.getobj(objid)
                    self.url_recurse(obj, urls)
                except Exception as ex:
                    print(ex)
                    continue

        http_uris = []
        # Non web URI's e.g file handles are embedded javascript to href.
        non_http_uris = []

        for u in urls:
            # Verify urls
            try:
                httpUrlValidator.validate_python(u)
            except ValidationError:
                non_http_uris.append(u)
                continue
            http_uris.append(u)

        # did we produce textual content?
        output = outfp.getvalue()
        if output:
            self.add_text(output)
        self.add_feature_values("pdf_embedded_uri", list(http_uris))
        self.add_feature_values("pdf_embedded_non_http_uri", list(non_http_uris))

    def url_recurse(self, obj: dict | list | PDFStream | None, urls: set[str]):
        """Recurse through pdf obj tree looking for URI's."""
        if not obj:
            return

        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "URI" and isinstance(v, bytes):
                    urls.add(v.decode("utf-8"))
                self.url_recurse(v, urls)
        elif isinstance(obj, list):
            for v in obj:
                self.url_recurse(v, urls)
        elif isinstance(obj, PDFStream):
            self.url_recurse(obj.attrs, urls)


def main():
    """Run plugin via command-line."""
    cmdline_run(plugin=AzulPluginPdfText)


if __name__ == "__main__":
    main()
