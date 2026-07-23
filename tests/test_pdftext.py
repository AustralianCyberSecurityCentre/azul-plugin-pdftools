"""
pdftext test suite
==================

Test the pdftext plugin's ability to extract URI's and text.

"""

from azul_runner import Event, EventData
from azul_runner import FeatureValue as FV
from azul_runner import JobResult, State, Uri, test_template

from azul_plugin_pdftools.pdftext_plugin import AzulPluginPdfText


class TestExecute(test_template.TestPlugin):
    PLUGIN_TO_TEST = AzulPluginPdfText

    def test_pdf_nonencrypted(self):
        """Regular PDF file with hyperlink - no encryption"""
        result = self.do_execution(
            data_in=[
                (
                    "content",
                    self.load_test_file_bytes(
                        "fb5757c13b6be5ddfcc5df34110bd742ec39d572fc12090af877b842e6569026",
                        "PDF with additional data appended to it.",
                    ),
                )
            ],
        )
        self.assertJobResult(
            result,
            JobResult(
                state=State(State.Label.COMPLETED),
                events=[
                    Event(
                        sha256="fb5757c13b6be5ddfcc5df34110bd742ec39d572fc12090af877b842e6569026",
                        data=[
                            EventData(
                                hash="bac199e7184664a42aacec177767c0be390d635beab3d3194acd6770623869dd", label="text"
                            )
                        ],
                        features={"pdf_embedded_uri": [FV(Uri("http://www.google.com/"))]},
                    )
                ],
                data={
                    "bac199e7184664a42aacec177767c0be390d635beab3d3194acd6770623869dd": b"This is a test document\n\nhttp://www.google.com\n\n\x0c"
                },
            ),
            inspect_data=True,
        )

    def test_pdf_owner_encrypted(self):
        """PDF file with hyperlink - owner encryption (reversible)"""
        result = self.do_execution(
            data_in=[
                (
                    "content",
                    self.load_test_file_bytes(
                        "080f79a5c58bc092fc9b99939cb3db35232bb2dd02f2345b0a87e73b0bcf2366",
                        "PDF with encrypted owner password rc4.",
                    ),
                )
            ],
        )
        self.assertJobResult(
            result,
            JobResult(
                state=State(State.Label.COMPLETED),
                events=[
                    Event(
                        sha256="080f79a5c58bc092fc9b99939cb3db35232bb2dd02f2345b0a87e73b0bcf2366",
                        data=[
                            EventData(
                                hash="bac199e7184664a42aacec177767c0be390d635beab3d3194acd6770623869dd", label="text"
                            )
                        ],
                        features={"pdf_embedded_uri": [FV(Uri("http://www.google.com/"))]},
                    )
                ],
                data={
                    "bac199e7184664a42aacec177767c0be390d635beab3d3194acd6770623869dd": b"This is a test document\n\nhttp://www.google.com\n\n\x0c"
                },
            ),
            inspect_data=True,
        )

    def test_pdf_user_encrypted(self):
        """PDF file with hyperlink - user encryption (need password)"""
        result = self.do_execution(
            data_in=[
                (
                    "content",
                    self.load_test_file_bytes(
                        "36abae6e31d591ab08a99c7b30bcb8dc3f208fa625f189c594eaf4caee1de394",
                        "Password protected PDF with embedded hyperlink.",
                    ),
                )
            ],
        )
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

    def test_pdf_malformed_pdf_that_cant_be_parsed(self):
        """PDF that fails parsing because it's malformed."""
        result = self.do_execution(
            data_in=[
                (
                    "content",
                    self.load_test_file_bytes(
                        "10bb21189de031c43b63747f2030d00031c06570787c38a0df6facb9ea1b0b2d",
                        "Malicious PDF, launch-action.",
                    ),
                )
            ],
        )
        self.assertJobResult(
            result,
            JobResult(
                state=State(State.Label.COMPLETED_WITH_ERRORS, message="Malformed PDF that failed parsing."),
                events=[
                    Event(
                        sha256="10bb21189de031c43b63747f2030d00031c06570787c38a0df6facb9ea1b0b2d",
                        features={"malformed": [FV("Malformed PDF that failed parsing.")]},
                    )
                ],
            ),
            inspect_data=True,
        )

    def test_pdf_regular_weird_uri_feature(self):
        """Regular PDF file but it's uri features are complex"""
        result = self.do_execution(
            data_in=[
                (
                    "content",
                    self.load_test_file_bytes(
                        "ca36e3321a09282ddfadc4a891dc02ddf3b4c6c45046bfd4b7baf99e151323a7",
                        "Benign PDF with complex URIs.",
                    ),
                )
            ],
        )
        self.assertJobResult(
            result,
            JobResult(
                state=State(State.Label.COMPLETED),
                events=[
                    Event(
                        sha256="ca36e3321a09282ddfadc4a891dc02ddf3b4c6c45046bfd4b7baf99e151323a7",
                        data=[
                            EventData(
                                hash="61e31863f8847980ed211819431c3caf2eccf3d20edca9591498d2b26c5416a2", label="text"
                            )
                        ],
                        features={
                            "pdf_embedded_non_http_uri": [
                                FV(
                                    "javascript:openAWindow('../../../docs_e/legal_e/26-gats_01_e.htm#articleX','',screen.width*0.7,screen.height*0.6,1)"
                                ),
                                FV(
                                    "javascript:openAWindow('../../../docs_e/legal_e/26-gats_01_e.htm#articleXIII','',screen.width*0.7,screen.height*0.6,1)"
                                ),
                                FV(
                                    "javascript:openAWindow('../../../docs_e/legal_e/26-gats_01_e.htm#articleXIV','',screen.width*0.7,screen.height*0.6,1)"
                                ),
                                FV(
                                    "javascript:openAWindow('../../../docs_e/legal_e/26-gats_01_e.htm#articleXV','',screen.width*0.7,screen.height*0.6,1)"
                                ),
                                FV(
                                    "javascript:openAWindow('../../../docs_e/legal_e/26-gats_01_e.htm#articleXXI','',screen.width*0.7,screen.height*0.6,1)"
                                ),
                            ],
                            "pdf_embedded_uri": [
                                FV(
                                    "http://journals.cambridge.org/action/displayFulltext?type=6&fid=1220880&jid=WTR&volumeId=6&issueId=02&aid=1220876&fulltextType=RA&fileId=S1474745607003217##"
                                ),
                                FV(
                                    "http://uk.westlaw.com/find/default.wl?vc=0&rp=%2ffind%2fdefault.wl&DB=PROFILER%2DWLD&DocName=0322800201&FindType=h&AP=&fn=_top&rs=WLUK6.11&mt=WestlawUK&vr=2.0&sv=Split&sp=ukatlse-000"
                                ),
                                FV("http://www.law.uchicago.edu/Lawecon/index.html"),
                            ],
                        },
                    )
                ],
                data={"61e31863f8847980ed211819431c3caf2eccf3d20edca9591498d2b26c5416a2": b""},
            ),
        )
