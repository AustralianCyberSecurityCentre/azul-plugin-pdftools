"""Analyse PDF's using poppler-tools pdfinfo utility."""

from datetime import datetime
from tempfile import NamedTemporaryFile

from azul_runner import BinaryPlugin, Feature, Job, add_settings, cmdline_run

from .pdfinfo import EncryptedError, ExecutionError
from .pdfinfo import PDFInfo as Parser


class AzulPluginPdfInfo(BinaryPlugin):
    """Analyse PDF's using poppler-tools pdfinfo utility."""

    CONTACT = "ASD's ACSC"
    VERSION = "2025.03.19"
    SETTINGS = add_settings(
        filter_data_types={"content": ["document/pdf", "document/pdf/"]},
    )
    FEATURES = [
        Feature("document_title", desc="Document title", type=str),
        Feature("document_author", desc="Document author name", type=str),
        Feature("document_company", desc="Company name of user who authored the document", type=str),
        Feature("document_created", desc="Time the document was created", type=datetime),
        Feature("document_last_saved", desc="Time the document was last saved", type=datetime),
        Feature("document_page_count", desc="Count of pages in the document", type=int),
        Feature("pdf_author", desc="Author of the PDF document", type=str),
        Feature("pdf_title", desc="Title of the PDF document", type=str),
        Feature("pdf_version", desc="PDF Version extracted from document header", type=str),
        Feature("pdf_page_rotation", desc="Rotation of page layout in degrees", type=int),
        Feature("pdf_page_size", desc="Page dimensions for the document", type=str),
        Feature("pdf_page_count", desc="Number of pages in the PDF document", type=int),
        Feature("pdf_date_created", desc="Creation timestamp of the PDF document", type=datetime),
        Feature("pdf_date_modified", desc="Last modified timestamp of the PDF document", type=datetime),
        Feature("pdf_producer", desc="Application/library that produced the PDF", type=str),
        Feature("pdf_creator", desc="Application/library that created the PDF", type=str),
        Feature("pdf_form_name", desc="Form template used for the PDF document", type=str),
        Feature("pdf_encryption", desc="Encryption algorithm used to protect the document", type=str),
        Feature("pdf_keyword", desc="Keywords stored in properties for the PDF document", type=str),
        Feature("processing_failure", desc="Error when attempting to parse the document", type=str),
        Feature("tag", desc="An informational label about the document", type=str),
    ]

    def execute(self, job: Job):
        """Run pdfinfo tool across binary."""
        self.features = {}
        with NamedTemporaryFile(delete=True) as tmp:
            tmp.write(job.get_data().read())
            tmp.flush()
            try:
                meta = Parser(tmp.name).info
            except EncryptedError:
                self.add_feature_values("tag", "encrypted_pdf")
                return
            except ExecutionError as ex:
                raise ex

        self.meta_to_feature(meta, "PDF version", "pdf_version")
        self.meta_to_feature(meta, "Author", "pdf_author")
        self.meta_to_feature(meta, "Title", "pdf_title")
        self.meta_to_feature(meta, "Creator", "pdf_creator")
        self.meta_to_feature(meta, "Producer", "pdf_producer")
        self.meta_to_feature(meta, "CreationDate", "pdf_date_created")
        self.meta_to_feature(meta, "ModDate", "pdf_date_modified")
        self.meta_to_feature(meta, "Page size", "pdf_page_size")
        self.meta_to_feature(meta, "Pages", "pdf_page_count")
        self.meta_to_feature(meta, "Page rot", "pdf_page_rotation")
        self.meta_to_feature(meta, "Encryption Algorithm", "pdf_encryption")

        # don't set if pdfinfo reports 'none'
        if meta.get("Form", "none") != "none":
            self.meta_to_feature(meta, "Form", "pdf_form_name")

        # Keywords is a list
        for x in meta.get("Keywords", []):
            self.features.setdefault("pdf_keyword", []).append(x)

        # boolean flags
        self.add_tag(meta, "Encrypted", "encrypted_pdf")
        self.add_tag(meta, "Optimized", "optimized_pdf")
        self.add_tag(meta, "Tagged", "tagged_pdf")
        self.add_tag(meta, "JavaScript", "javascript_pdf")

        # just flag that there were parser errors of some kind
        if meta.get("Errors"):
            self.features["processing_failure"] = "pdfinfo_parse_error"

        # common, authored document properties
        self.meta_to_feature(meta, "Author", "document_author")
        self.meta_to_feature(meta, "Title", "document_title")
        self.meta_to_feature(meta, "CreationDate", "document_created")
        self.meta_to_feature(meta, "ModDate", "document_last_saved")
        self.meta_to_feature(meta, "Pages", "document_page_count")
        self.add_many_feature_values(self.features)

    def meta_to_feature(self, meta, meta_name, feature_name):
        """Map features from json metadata output."""
        val = meta.get(meta_name)
        if not val:
            return

        feat = None
        for f in self.FEATURES:
            if f.name == feature_name:
                feat = f
                break
        if not feat:
            return

        if val and feat.type == int:
            val = int(val)

        self.features.setdefault(feature_name, []).append(val)

    def add_tag(self, meta, meta_name, tag_name):
        """Set a named tag on the sample based on metadata dict."""
        val = meta.get(meta_name)
        if val:
            self.features.setdefault("tag", []).append(tag_name)


def main():
    """Run plugin via command-line."""
    cmdline_run(plugin=AzulPluginPdfInfo)


if __name__ == "__main__":
    main()
