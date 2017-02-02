import os
import re
import logging


class FileHandler():
    def __init__(self, path):
        self.path = path
        self.exists = os.path.exists(self.path)
        self.format = ""
        self.headers = {}
        self.post_content = ""
        self.raw_content = ""

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

class MarkdownHandler(FileHandler):
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
        output.append("Title: {}".format(self.headers["title"]))
        output.append("Slug: {}".format(self.headers["slug"]))
        output.append("Date: {}".format(self.headers["date"]))
        if "modified" in self.headers:
            output.append("Modified: {}".format(self.headers["modified"]))
        output.append("Category: {}".format(self.headers["category"]))
        output.append("Tags: {}".format(self.headers["tags"]))
        if "authors" in self.headers:
            output.append("Authors: {}".format(self.headers["authors"]))
        if "summary" in self.headers:
            output.append("Summary: {}".format(self.headers["summary"]))

        return "\n".join(output)
