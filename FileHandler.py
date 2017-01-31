import os
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
        stream_handle.write("\n")
        stream_handle.write(self.post_content)

class MarkdownHandler(FileHandler):
    def __init__(self, path):
        super(MarkdownHandler, self).__init__(path)

    def read_stream(self, stream_handle):
        self.raw_content = stream_handle.read()
        for line in self.raw_content.split("\n"):
            kv = line.split(':')
            if len(kv) != 2:
                continue

            name, values = kv[0].lower(), kv[1].strip()
            # Feeble attempt to skip lines that aren't real metadata
            if " " in name or "http" in name:
                continue
            logging.debug("Metadata {name}: {values}".format(name=name, values=values))

            if name in ['tags', 'category', 'author', 'authors']:
                if name == 'author':
                    name = 'authors'

                if ';' in values:
                    values = values.split(';')
                else:
                    values = values.split(',')

                # TODO: I guess we don't support empty values? pelican does this a bit different
                values = [v.strip() for v in values]

                self.headers[name] = values

    @property
    def formatted_headers(self):
        output = []
        output.append("Title: {}".format(self.headers["title"]))
        output.append("Slug: {}".format(self.headers["slug"]))
        output.append("Date: {}".format(self.headers["date"]))
        if "modified" in self.headers:
            output.append("Modified: {}".format(self.headers["modified"]))
        output.append("Category: {}".format(self.headers["category"]))
        output.append("Tags: {}".format(", ".join(sorted(self.headers["tags"], key=str.lower))))
        if "authors" in self.headers:
            output.append("Authors: {}".format("; ".join(self.headers["authors"])))
        if "summary" in self.headers:
            output.append("Summary: {}".format(self.headers["summary"]))

        return "\n".join(output)
