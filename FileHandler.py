import os
import re
import logging


class Factory():
    """
    Public class to be used by clients.
    It instantiates and returns concrete FileHandler class.
    """

    def __init__(self, path, file_format=None):
        self.path = path
        self.file_format = file_format
        self.handler = self._choose_handler()

    def _choose_handler(self):
        if not self.file_format:
            _, ext = os.path.splitext(self.path)
            if ext in ['.md', '.markdown', '.mdown', '.mkd']:
                self.file_format = 'markdown'

        if self.file_format == "markdown":
            return MarkdownHandler
        else:
            raise NotImplementedError("File format not supported")

    def generate(self):
        return self.handler(self.path)


class AbstractFileHandler():
    """
    Abstract class that defines interface used by classes resposible for
    reading files
    """
    def __init__(self, path):
        self.path = os.path.realpath(path)
        self.exists = os.path.exists(self.path) and os.path.isfile(self.path)
        self.format = ""
        self.headers = {}
        self.post_content = ""
        self.raw_content = ""

        self.read()

    def has_metadata(self):
        return bool(self.headers)

    def read(self):
        if not self.exists:
            return

        with open(self.path, "r") as fh:
            self.read_stream(fh)

    def read_stream(self, stream_handle):
        """ Child classes are expected to override this method """
        pass

    @property
    def formatted_headers(self):
        """ Child classes are expected to override this method """
        pass

    def prepend_headers(self):
        with open(self.path, "w") as fh:
            self.prepend_headers_stream(fh)

    def prepend_headers_stream(self, stream_handle):
        stream_handle.write(self.formatted_headers)
        stream_handle.write("\n\n")
        stream_handle.write(self.raw_content)

    def overwrite_headers(self):
        with open(self.path, "w") as fh:
            self.overwrite_headers_stream(fh)

    def overwrite_headers_stream(self, stream_handle):
        stream_handle.write(self.formatted_headers)
        stream_handle.write("\n\n")
        stream_handle.write(self.post_content)

class MarkdownHandler(AbstractFileHandler):
    def __init__(self, path):
        super(MarkdownHandler, self).__init__(path)

    def read_stream(self, stream_handle):
        META_RE = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
        META_MORE_RE = re.compile(r'^[ ]{4,}(?P<value>.*)')
        BEGIN_RE = re.compile(r'^-{3}(\s.*)?')
        END_RE = re.compile(r'^(-{3}|\.{3})(\s.*)?')

        raw_content = []
        post_content = []
        processed_headers = False

        for line in stream_handle:
            raw_content.append(line)

            if processed_headers:
                post_content.append(line)
                continue

            if BEGIN_RE.match(line):
                continue

            m1 = META_RE.match(line)
            if m1:
                key = m1.group('key').lower().strip()
                value = m1.group('value').strip()
                # We have mis-interpreted URL as key-value pair
                if value.startswith("//"):
                    processed_headers = True
                    post_content.append(line)
                else:
                    self.headers[key] = value
                continue

            m2 = META_MORE_RE.match(line)
            if m2 and key:
                self.headers[key] = "{}; {}".format(self.headers[key], m2.group('value').strip())
                continue

            if line.strip() == '' or END_RE.match(line) or not m1:
                processed_headers = True
                if line.strip() != '':
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
