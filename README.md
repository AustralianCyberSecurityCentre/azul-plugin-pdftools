# Azul Plugin Pdftools

Plugins for extracting features and text from Adobe PDF files.

Note: See also _azul-unbox_ for password protected PDF decryption and
stream extraction.

## Development Installation

To install azul-plugin-pdftools for development run the command
(from the root directory of this project):

```
apt-get install poppler-utils
pip install -e .
```

## Usage: azul-pdfid

Uses _Didier Steven's_ pdfid script to extract features and entropy about
PDF document streams.

Usage on local files:

```
azul-pdfid test.pdf
```

Example Output:

```
----- PdfId results -----
OK

Output features:
  pdf_entropy_nonstream: 5.305706
     pdf_entropy_stream: 7.959999
      pdf_keyword_count: /Page - 1
                         startxref - 2
                         /ObjStm - 4
                         endstream - 23
                         stream - 23
                         endobj - 26
                         obj - 27
            pdf_version: %PDF-1.5
          pdf_eof_count: 2
      pdf_entropy_total: 7.954224
         pdf_date_field: /pdf - D:20141022122901

Feature key:
  pdf_date_field:  Timestamp field appearing in document
  pdf_entropy_nonstream:  Entropy across contents outside of streams
  pdf_entropy_stream:  Entropy across stream data
  pdf_entropy_total:  Entropy across entire document contents
  pdf_eof_count:  Count of PDF %%EOF markers
  pdf_keyword_count:  Number of times the labelled keyword appears in document
  pdf_version:  PDF version header
```

Automated usage in system:

```bash
azul-pdfid --server http://azul-dispatcher.localnet/
```

## Usage: azul-pdfinfo

Users the _pdfinfo_ command from the _poppler-utils_ package to extract
PDF document metadata as features.

Usage on local files:

```bash
azul-pdfinfo test.pdf
```

Example Output:

```bash
----- PdfInfo results -----
OK

Output features:
  document_last_saved: 2014-10-22 14:29:11
    pdf_date_modified: 2014-10-22 14:29:11
        pdf_page_size: 595.32 x 841.92 pts (A4)
                  tag: optimized_pdf
                       tagged_pdf
      document_author: Vb1
          pdf_version: 1.5
          pdf_creator: Acrobat PDFMaker 11 für Word
  document_page_count: 1
     document_created: 2014-10-22 14:29:10
       pdf_page_count: 1
         pdf_producer: Adobe PDF Library 11.0
     pdf_date_created: 2014-10-22 14:29:10
           pdf_author: Vb1

Feature key:
  document_author:  Document author name
  document_created:  Time the document was created
  document_last_saved:  Time the document was last saved
  document_page_count:  Count of pages in the document
  pdf_author:  Author of the PDF document
  pdf_creator:  Application/library that created the PDF
  pdf_date_created:  Creation timestamp of the PDF document
  pdf_date_modified:  Last modified timestamp of the PDF document
  pdf_page_count:  Number of pages in the PDF document
  pdf_page_size:  Page dimensions for the document
  pdf_producer:  Application/library that produced the PDF
  pdf_version:  PDF Version extracted from document header
  tag:  An informational label about the document
```

Automated usage in system:

```bash
azul-pdfinfo --server http://azul-dispatcher.localnet/
```

## Usage: azul-pdftext

Uses _pdfminer_ python library to convert PDF to readable text and raise as
a search indexable stream.

Usage on local files:

```bash
azul-pdftext test.pdf
```

Example Output:

```bash
----- PdfText results -----
OK

Output features:
  pdf_embedded_uri: http://creativecommons.org/licenses/by-sa/3.0/
                    http://en.wikipedia.org/wiki/John_Doe
                    http://www.online-convert.com/
                    http://www.online-convert.com/file-type

Feature key:
  pdf_embedded_uri:  URI link embedded in the PDF document

```

Automated usage in system:

```bash
azul-pdftext --server http://azul-dispatcher.localnet/
```

## Python Package management

This python package is managed using a `setup.py` and `pyproject.toml` file.

Standardisation of installing and testing the python package is handled through tox.
Tox commands include:

```bash
# Run all standard tox actions
tox
# Run linting only
tox -e style
# Run tests only
tox -e test
```

## Dependency management

Dependencies are managed in the requirements.txt, requirements_test.txt and debian.txt file.

The requirements files are the python package dependencies for normal use and specific ones for tests
(e.g pytest, black, flake8 are test only dependencies).

The debian.txt file manages the debian dependencies that need to be installed on development systems and docker images.

Sometimes the debian.txt file is insufficient and in this case the Dockerfile may need to be modified directly to
install complex dependencies.
