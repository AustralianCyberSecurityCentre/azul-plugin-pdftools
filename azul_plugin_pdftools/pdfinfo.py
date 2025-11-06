"""Python wrapper around poppler-utils pdfinfo command-line tool."""

import os
import re
import subprocess  # noqa: S404 # nosec B404
from datetime import datetime

# installation check
try:
    subprocess.Popen(  # noqa: S603, S607 # nosec B603 B607
        ["pdfinfo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).communicate()
except OSError as err:
    msg = [
        "error = %s" % err,
        "PdfInfo requires the program 'pdfinfo' to be installed.",
        "Please run apt-get install poppler-utils",
    ]
    raise ImportError("\n".join(msg))


def convert_bool(string):
    """Convert string to bool handling several representations."""
    if string.lower() in ("yes", "true"):
        return True
    return False


def convert_datetime(string):
    """Convert string to datetime in UTC."""
    try:
        # newer versions handle timezones correctly and convert to UTC
        if string.endswith("UTC"):
            # Timezone aware parsing
            return datetime.strptime(string, "%a %b %d %H:%M:%S %Y UTC")
        return datetime.strptime(string, "%a %b %d %H:%M:%S %Y")
    except Exception:
        return None


def convert_keywords(string):
    """Convert comma-separated string into list of strings."""
    return [x.strip() for x in string.split(",") if x.strip()]


class PDFInfoError(Exception):
    """Base PDFInfo exception type."""


class ExecutionError(PDFInfoError):
    """Unable to execute the pdfinfo command-line tool for some reason."""

    def __init__(self, msg, stderr=""):
        """Wrap the stderr from pdfinfo as an exception."""
        PDFInfoError.__init__(self, msg)
        self.stderr = stderr


class EncryptedError(PDFInfoError):
    """Has unknown user password, can't decrypt."""

    def __init__(self, msg, stderr=""):
        """Wrap the stderr from pdfinfo as an exception."""
        PDFInfoError.__init__(self, msg)
        self.stderr = stderr


class PDFInfo(object):
    """Encapsulates running pdfinfo tool and parsing its output."""

    # mapping of non-string key names -> data type func
    meta_types = {
        "CreationDate": convert_datetime,
        "ModDate": convert_datetime,
        "Tagged": convert_bool,
        "Optimized": convert_bool,
        "UserProperties": convert_bool,
        "Suspects": convert_bool,
        "JavaScript": convert_bool,
        "Keywords": convert_keywords,
        # needs further processing - 'Encrypted': convert_bool,
        "Pages": int,
        "Page rot": int,
        # could parse boxes into (x, y, h, w) too
        # but don't really have a need yet
    }

    def __init__(self, path, opw="", upw=""):
        """Run pdfinfo on the supplied file path.

        Optionally handle user and owner passwords for encrypted PDFs.
        Resultant metadata is available in `info` attribute.
        """
        cmd = ["pdfinfo"]
        cmd += ["-opw", opw]
        cmd += ["-upw", upw]
        cmd.append("-box")
        cmd.append(path)
        env = dict(os.environ)
        env["TZ"] = "UTC"
        p = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # noqa: S603 # nosec B603
        stdout, stderr = p.communicate()
        # convert bytes to strings
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")
        if "Incorrect password" in stderr:
            raise EncryptedError("Incorrect password for encrypted pdf", stderr)
        if p.returncode:
            raise ExecutionError("pdfinfo returned error", stderr)

        self.info = {"Errors": []}
        for x in stdout.splitlines():
            if not x.strip():
                continue
            # break apart key: value strings
            key = x.split(":", 1)[0].strip()
            value = x.split(":", 1)[1].strip()

            # special handling for some fields
            if key == "Encrypted":
                # if true contains extra information
                m = re.match(
                    r"yes \(print:(\w+) copy:(\w+) change:(\w+) " r"addNotes:(\w+) algorithm:([\-\w]+)\)", value
                )
                if m:
                    value = True
                    self.info["Encryption Allow Print"] = convert_bool(m.group(1))
                    self.info["Encryption Allow Copy"] = convert_bool(m.group(2))
                    self.info["Encryption Allow Edit"] = convert_bool(m.group(3))
                    self.info["Encryption Allow Add Notes"] = convert_bool(m.group(4))
                    self.info["Encryption Algorithm"] = m.group(5)
                else:
                    value = False
            # type conversions
            if key in PDFInfo.meta_types:
                value = PDFInfo.meta_types[key](value)
            self.info[key] = value
        # errors
        for x in stderr.splitlines():
            if not x.strip():
                continue
            self.info["Errors"].append(x.strip())
