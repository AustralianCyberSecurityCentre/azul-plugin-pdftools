"""
PdfId Plugin Tests
==================
"""

from azul_runner import Event
from azul_runner import FeatureValue as FV
from azul_runner import JobResult, State, test_template

from azul_plugin_pdftools.pdfid_plugin import AzulPluginPdfId


class TestExecute(test_template.TestPlugin):
    PLUGIN_TO_TEST = AzulPluginPdfId

    def test_appended_data(self):
        """A PDF with trailing bytes appended"""
        result = self.do_execution(
            data_in=[
                (
                    "content",
                    self.load_test_file_bytes(
                        "fb5757c13b6be5ddfcc5df34110bd742ec39d572fc12090af877b842e6569026",
                        "PDF with additional data appended to it.",
                    ),
                )
            ]
        )
        self.assertEqual(result.state, State())
        self.assertJobResult(
            result,
            JobResult(
                state=State(State.Label.COMPLETED),
                events=[
                    Event(
                        sha256="fb5757c13b6be5ddfcc5df34110bd742ec39d572fc12090af877b842e6569026",
                        features={
                            "pdf_date_field": [FV("D:20151209105252+11'00", label="/CreationDate")],
                            "pdf_entropy_nonstream": [FV("4.726555")],
                            "pdf_entropy_stream": [FV("7.974126")],
                            "pdf_entropy_total": [FV("7.458206")],
                            "pdf_eof_count": [FV("1")],
                            "pdf_keyword_count": [
                                FV("1", label="/OpenAction"),
                                FV("1", label="/Page"),
                                FV("1", label="startxref"),
                                FV("1", label="trailer"),
                                FV("1", label="xref"),
                                FV("16", label="endobj"),
                                FV("16", label="obj"),
                                FV("2", label="/URI"),
                                FV("4", label="endstream"),
                                FV("4", label="stream"),
                            ],
                            "pdf_trailing_bytes": [FV("2273")],
                            "pdf_version": [FV("%PDF-1.4")],
                        },
                    )
                ],
            ),
        )

    def test_pdf_password(self):
        """
        Encrypted/passworded PDF
        """
        result = self.do_execution(
            data_in=[
                (
                    "content",
                    self.load_test_file_bytes(
                        "36abae6e31d591ab08a99c7b30bcb8dc3f208fa625f189c594eaf4caee1de394",
                        "Password protected PDF with embedded hyperlink.",
                    ),
                )
            ]
        )
        self.assertEqual(result.state, State())
        self.assertJobResult(
            result,
            JobResult(
                state=State(State.Label.COMPLETED),
                events=[
                    Event(
                        entity_type="binary",
                        entity_id="36abae6e31d591ab08a99c7b30bcb8dc3f208fa625f189c594eaf4caee1de394",
                        features={
                            "pdf_entropy_nonstream": [FV(5.070577)],
                            "pdf_entropy_stream": [FV(7.976922)],
                            "pdf_entropy_total": [FV(7.755079)],
                            "pdf_eof_count": [FV(1)],
                            "pdf_keyword_count": [
                                FV(1, label="/Encrypt"),
                                FV(1, label="/OpenAction"),
                                FV(1, label="/Page"),
                                FV(1, label="startxref"),
                                FV(1, label="trailer"),
                                FV(1, label="xref"),
                                FV(2, label="/URI"),
                                FV(4, label="endstream"),
                                FV(4, label="stream"),
                                FV(15, label="endobj"),
                                FV(15, label="obj"),
                            ],
                            "pdf_version": [FV("%PDF-1.4")],
                            "tag": [FV("encrypted_pdf")],
                        },
                    )
                ],
            ),
        )

    def test_not_pdf(self):
        """
        Wrong File type
        """
        result = self.do_execution(
            data_in=[
                (
                    "content",
                    self.load_test_file_bytes(
                        "15c8614f493cf081b53ea379b06d759fc51cf94d61d245baab5efb77648bf8d4", "Benign RTF file."
                    ),
                )
            ],
            verify_input_content=False,
        )
        self.assertEqual(result.state, State(State.Label.OPT_OUT))

    def test_pdf_with_na_entropy_stream(self):
        """
        PDF that contains streams with an entropy of N/A.
        """
        result = self.do_execution(
            data_in=[
                (
                    "content",
                    self.load_test_file_bytes(
                        "4d344e92a23c84984e53012b89425958983cb0fd6a76a9e9236f6e1fa64a6d8b",
                        "Malicious PDF, with na entropy stream.",
                    ),
                )
            ],
            verify_input_content=False,
        )
        self.assertJobResult(
            result,
            JobResult(
                state=State(State.Label.COMPLETED),
                events=[
                    Event(
                        entity_type="binary",
                        entity_id="4d344e92a23c84984e53012b89425958983cb0fd6a76a9e9236f6e1fa64a6d8b",
                        features={
                            "pdf_entropy_nonstream": [FV(3.276496)],
                            "pdf_entropy_total": [FV(3.276496)],
                            "pdf_eof_count": [FV(1)],
                            "pdf_keyword_count": [
                                FV(1, label="/Launch"),
                                FV(1, label="/OpenAction"),
                                FV(1, label="/Page"),
                                FV(1, label="startxref"),
                                FV(1, label="trailer"),
                                FV(1, label="xref"),
                                FV(5, label="endobj"),
                                FV(5, label="obj"),
                            ],
                            "pdf_keyword_hex_count": [
                                FV(1, label="/Launch"),
                                FV(1, label="/OpenAction"),
                                FV(1, label="/Page"),
                            ],
                            "pdf_version": [FV("%PDF-1.5")],
                        },
                    )
                ],
            ),
        )
