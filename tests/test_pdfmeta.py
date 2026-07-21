"""
PDFInfo Plugin Tests
====================
"""

import datetime

from azul_runner import Event
from azul_runner import FeatureValue as FV
from azul_runner import JobResult, State, test_template

from azul_plugin_pdftools.pdfmeta_plugin import AzulPluginPdfInfo


class TestExecute(test_template.TestPlugin):
    PLUGIN_TO_TEST = AzulPluginPdfInfo

    def test_unencrypted_pdf(self):
        """An unencrypted PDF"""
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
                            "document_created": [FV(datetime.datetime(2015, 12, 8, 23, 52, 52))],
                            "document_page_count": [FV(1)],
                            "pdf_creator": [FV("Writer")],
                            "pdf_date_created": [FV(datetime.datetime(2015, 12, 8, 23, 52, 52))],
                            "pdf_page_count": [FV(1)],
                            "pdf_page_size": [FV("595 x 842 pts (A4)")],
                            "pdf_producer": [FV("LibreOffice 4.2")],
                            "pdf_version": [FV("1.4")],
                        },
                    )
                ],
            ),
        )

    def test_pdf_owner_password(self):
        """
        Encrypted PDF - owner password (easily reversed)
        """
        result = self.do_execution(
            data_in=[
                (
                    "content",
                    self.load_test_file_bytes(
                        "080f79a5c58bc092fc9b99939cb3db35232bb2dd02f2345b0a87e73b0bcf2366",
                        "PDF with encrypted owner password rc4.",
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
                        sha256="080f79a5c58bc092fc9b99939cb3db35232bb2dd02f2345b0a87e73b0bcf2366",
                        features={
                            "document_created": [FV(datetime.datetime(2015, 12, 8, 23, 52, 52))],
                            "document_page_count": [FV(1)],
                            "pdf_creator": [FV("Writer")],
                            "pdf_date_created": [FV(datetime.datetime(2015, 12, 8, 23, 52, 52))],
                            "pdf_encryption": [FV("RC4")],
                            "pdf_page_count": [FV(1)],
                            "pdf_page_size": [FV("595 x 842 pts (A4)")],
                            "pdf_producer": [FV("LibreOffice 4.2")],
                            "pdf_version": [FV("1.4")],
                            "tag": [FV("encrypted_pdf")],
                        },
                    )
                ],
            ),
        )

    def test_pdf_user_password(self):
        """
        Encrypted PDF - user password (need password to open).
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
                        sha256="36abae6e31d591ab08a99c7b30bcb8dc3f208fa625f189c594eaf4caee1de394",
                        features={"tag": [FV("encrypted_pdf")]},
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
        self.assertEqual(result.state.label, State.Label.ERROR_EXCEPTION)
