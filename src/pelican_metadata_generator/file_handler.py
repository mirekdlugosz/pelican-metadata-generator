import os
import re


class Factory:
    """
    Public-facing class that chooses appropriate FileHandler class for users

    Note
    ----
    You should call ``generate`` immediately after instantiating this class.

    Parameters
    ----------
    path
        Path to file (FileHandler will be chosen based on extension).
    file_format
        Required format of FileHandler.
    """

    def __init__(self, path, file_format=None):
        self.path = path
        self.file_format = file_format
        self.handler = self._choose_handler()

    def _choose_handler(self):
        """Chooses and returns FileHandler object based on extension or user request"""
        if not self.file_format:
            _, ext = os.path.splitext(self.path)
            if ext in [".md", ".markdown", ".mdown", ".mkd"]:
                self.file_format = "markdown"
            elif ext in [".rst"]:
                self.file_format = "restructuredtext"

        if self.file_format == "markdown":
            return MarkdownHandler
        elif self.file_format == "restructuredtext":
            return RestructuredtextHandler
        else:
            raise NotImplementedError("File format not supported: {}".format(self.file_format))

    def generate(self):
        """Returns instantiated FileHandler object"""
        return self.handler(self.path)


class AbstractFileHandler:
    """
    Abstract class that defines interface used by classes responsible for
    reading files. It is not intended to be used directly - rather, specific
    file formats should subclass it.

    Parameters
    ----------
    path
        Path to file (FileHandler will be chosen based on extension).
    """

    def __init__(self, path):
        self.path = os.path.realpath(path)
        self.exists = os.path.exists(self.path) and os.path.isfile(self.path)
        self.default_extension = ""
        self.format = ""
        self.headers = {}
        self.post_content = ""
        self.raw_content = ""

        self.read()

    def has_metadata(self):
        """True if file has metadata"""
        return bool(self.headers)

    def read(self):
        """Reads file content
        This method can be used to work with real files.
        """
        if not self.exists:
            return

        with open(self.path, "r", encoding="utf-8") as fh:
            self.read_stream(fh)

    def read_stream(self, stream_handle):
        """Reads and parses file format
        This method can be used to work with any object that provides
        file stream API.

        Note
        ----
        Child classes are expected to override this method
        """
        pass

    @property
    def formatted_headers(self):
        """Returns file metadata in given format as string

        Note
        ----
        Child classes are expected to override this method
        """
        pass

    def prepend_headers(self):
        """Adds file metadata at top of file (leaving existing metadata as-is)
        This method can be used to work with real files.
        """
        with open(self.path, "w", encoding="utf-8") as fh:
            self.prepend_headers_stream(fh)

    def prepend_headers_stream(self, stream_handle):
        """Adds file metadata at top of file (leaving existing metadata as-is)
        This method can be used to work with any object that provides
        file stream API.
        """
        stream_handle.write(self.formatted_headers)
        stream_handle.write("\n\n")
        stream_handle.write(self.raw_content)

    def overwrite_headers(self):
        """Adds file metadata at top of file (removing existing metadata)
        This method can be used to work with real files.
        """
        with open(self.path, "w", encoding="utf-8") as fh:
            self.overwrite_headers_stream(fh)

    def overwrite_headers_stream(self, stream_handle):
        """Adds file metadata at top of file (removing existing metadata)
        This method can be used to work with any object that provides
        file stream API.
        """
        stream_handle.write(self.formatted_headers)
        stream_handle.write("\n\n")
        stream_handle.write(self.post_content)


class MarkdownHandler(AbstractFileHandler):
    """Markdown metadata parser"""

    def __init__(self, path):
        super(MarkdownHandler, self).__init__(path)
        self.default_extension = "md"

    def read_stream(self, stream_handle):
        META_RE = re.compile(r"^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)")
        META_MORE_RE = re.compile(r"^[ ]{4,}(?P<value>.*)")
        BEGIN_RE = re.compile(r"^-{3}(\s.*)?")
        END_RE = re.compile(r"^(-{3}|\.{3})(\s.*)?")

        raw_content = []
        post_content = []
        processed_headers = False
        key = None

        for line in stream_handle:
            raw_content.append(line)

            if processed_headers:
                post_content.append(line)
                continue

            if BEGIN_RE.match(line):
                continue

            m1 = META_RE.match(line)
            if m1:
                key = m1.group("key").lower().strip()
                value = m1.group("value").strip()
                # We have mis-interpreted URL as key-value pair
                if value.startswith("//"):
                    processed_headers = True
                    post_content.append(line)
                else:
                    self.headers[key] = value
                continue

            m2 = META_MORE_RE.match(line)
            if m2 and key:
                self.headers[key] = "{}; {}".format(self.headers[key], m2.group("value").strip())
                continue

            if line.strip() == "" or END_RE.match(line) or not m1:
                processed_headers = True
                if line.strip() != "":
                    post_content.append(line)

        self.raw_content = "".join(raw_content)
        self.post_content = "".join(post_content)

    @property
    def formatted_headers(self):
        output = []
        for key in ["title", "slug", "date", "modified", "category", "tags", "authors", "summary"]:
            if key in self.headers:
                output.append("{}: {}".format(key.title(), self.headers[key]))

        return "\n".join(output)


class RestructuredtextHandler(AbstractFileHandler):
    """ReStructuredText metadata parser"""

    def __init__(self, path):
        super(RestructuredtextHandler, self).__init__(path)
        self.default_extension = "rst"

    def read_stream(self, stream_handle):
        META_RE = re.compile(r"^[ ]{0,3}:(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)")
        META_MORE_RE = re.compile(r"^[ ]{4,}-?\s*(?P<value>.*)")
        META_TITLE_RE = re.compile(r"^[=~_*+#-]+")

        raw_content = []
        post_content = []
        processed_headers = False
        key = None

        for line in stream_handle:
            raw_content.append(line)

            if processed_headers:
                post_content.append(line)
                continue

            if len([x for x in post_content if x.strip()]) > 1:
                processed_headers = True
                post_content.append(line)
                continue

            if META_TITLE_RE.match(line):
                self.headers["title"] = post_content.pop().strip()
                continue

            m1 = META_RE.match(line)
            if m1:
                key = m1.group("key").lower().strip()
                value = m1.group("value").strip()
                self.headers[key] = value
                continue

            m2 = META_MORE_RE.match(line)
            if m2 and key:
                value = m2.group("value").strip()
                if line.strip().startswith("-"):
                    self.headers[key] = "{}; {}".format(self.headers[key], value)
                    self.headers[key] = self.headers[key].lstrip("- ")
                else:
                    self.headers[key] = "{} {}".format(self.headers[key], value).strip()
                continue

            if line.strip() == "":
                if len(self.headers) > 1:
                    processed_headers = True
                continue

            # `not m1` part of this condition is implicit - we can reach
            # this point only if line does not match META_RE or META_MORE_RE
            if "title" in self.headers:
                processed_headers = True

            post_content.append(line)

        self.raw_content = "".join(raw_content)
        self.post_content = "".join(post_content)

    @property
    def formatted_headers(self):
        output = []
        if "title" in self.headers:
            output.append(self.headers["title"])
            output.append("#" * len(self.headers["title"]))
            output.append("")

        for key in ["slug", "date", "modified", "category", "tags", "authors", "summary"]:
            if key in self.headers:
                output.append(":{}: {}".format(key.lower(), self.headers[key]))

        return "\n".join(output)
