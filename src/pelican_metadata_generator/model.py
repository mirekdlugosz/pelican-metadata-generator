import os
import logging

from PyQt5 import QtCore

import pelican_metadata_generator.file_handler


class NewPostMetadata(QtCore.QObject):
    """Represents metadata of new post

    Attributes
    ----------
    title
        Post title
    slug
        Post slug (URL-safe identifier)
    date
        Created date
    modified
        Last modified date
    category
        Post category
    tags
        Post tags (list)
    authors
        Post authors (list)
    summary
        Post summary
    file_format
        File format. See pelican_metadata_generator.file_handler.Factory for supported file formats.
    """

    changed = QtCore.pyqtSignal()
    fileHasHeaders = QtCore.pyqtSignal()

    def __init__(self):
        super(NewPostMetadata, self).__init__(None)
        self.title = ""
        self.slug = ""
        self.date = ""
        self.modified = ""
        self.category = ""
        self.tags = []
        self.authors = []
        self.summary = ""
        self.file_format = ""

    @property
    def filename(self):
        """Returns file name based on file format"""
        ext = (
            pelican_metadata_generator.file_handler.Factory("", self.file_format)
            .generate()
            .default_extension
        )
        return "{}.{}".format(self.slug, ext)

    def set_title(self, value):
        self.title = value
        self.changed.emit()

    def set_slug(self, value):
        self.slug = value
        self.changed.emit()

    def set_created_date(self, value):
        self.date = value.toString("yyyy-MM-dd hh:mm:ss")
        self.changed.emit()

    def set_modified_date(self, value):
        if value:
            self.modified = value.toString("yyyy-MM-dd hh:mm:ss")
        else:
            self.modified = ""
        self.changed.emit()

    def set_category(self, value):
        self.category = value
        self.changed.emit()

    def add_tag(self, value):
        if value not in self.tags:
            self.tags.append(value)
        self.changed.emit()

    def remove_tag(self, value):
        self.tags.remove(value)
        self.changed.emit()

    def set_author(self, value):
        if not value:
            self.authors = []
        else:
            self.authors = [value]
        self.changed.emit()

    def set_summary(self, text):
        self.summary = text
        self.changed.emit()

    def set_file_format(self, file_format):
        self.file_format = file_format
        self.changed.emit()

    def to_file(self, filepath):
        """Main method used to save current metadata into file

        Note
        ----
        It reads file content in order to verify if file contains
        valid metadata. If it does, it does nothing.
        Instead, controller is responsible for asking user what should
        be done and calling appropriate method directly (adding headers
        at top of file or overwriting existing metadata).
        """
        self.file = pelican_metadata_generator.file_handler.Factory(
            filepath, self.file_format
        ).generate()

        if self.file.has_metadata():
            self.fileHasHeaders.emit()
        else:
            self.to_file_prepend_headers()

    def to_file_prepend_headers(self):
        """Adds metadata at top of file content (leaving existing metadata as-is)"""
        self.file.headers = self._format_headers_object()
        self.file.prepend_headers()

    def to_file_overwrite_headers(self):
        """Adds metadata in place of existing metadata"""
        self.file.headers = self._format_headers_object()
        self.file.overwrite_headers()

    def _format_headers_object(self):
        """Prepares dictionary of metadata to inject in FileHandler subclass"""
        headers = {}

        for key in ["tags", "authors"]:
            values = getattr(self, key)
            if not values:
                continue

            separator = ", "
            if any(["," in x for x in values]):
                separator = "; "

            headers[key] = separator.join(sorted(values, key=str.lower))

        for key in ["title", "slug", "date", "modified", "category", "summary"]:
            if getattr(self, key):
                headers[key] = getattr(self, key)

        return headers

    def as_pelican_header(self):
        """Returns current metadata as string, formatted according to file
        format rules"""
        file_ = pelican_metadata_generator.file_handler.Factory("", self.file_format).generate()
        file_.headers = self._format_headers_object()
        return file_.formatted_headers


class MetadataDatabase(QtCore.QObject):
    """Represents all known metadata values

    Attributes
    ----------
    category
        List of categories
    tags
        List of tags
    authors
        List of authors

        Note
        ----
        No parsing of author value is attempted.
        "John Doe" and "Doe, John" are considered not equal,
        even if they probably represent the same person.
    path
        Path of last read directory

        Note
        ----
        It is intended for internal use of model methods.
    """

    changed = QtCore.pyqtSignal()

    def __init__(self, path=None):
        super(MetadataDatabase, self).__init__(None)
        self.category = []
        self.tags = []
        self.authors = []
        self.path = []
        self.read_directory(path)

    def read_directory(self, path):
        """Reads metadata from files in directory

        Parameters
        ----------
        path
            Path of directory that should be read.
        """
        if not path:
            return

        path = os.path.abspath(path)
        if os.path.isdir(path):
            self._readPathFiles(path)
            self.path = path
            self.changed.emit()

    def _readPathFiles(self, path):
        for root, dirs, files in os.walk(path):
            for filename in files:
                self._parseFile(os.path.join(root, filename))

    def _parseFile(self, path):
        logging.debug("Processing {file}".format(file=path))

        try:
            post = pelican_metadata_generator.file_handler.Factory(path).generate()
        except NotImplementedError:
            msg = "Ignoring {file} because it has unsupported extension"
            logging.info(msg.format(file=path))
            return

        for header in post.headers:
            if header in ["tags", "category", "author", "authors"]:
                self._appendMeta(header, post.headers[header])

    def _appendMeta(self, name, values):
        """
        This takes string that is metadata tag value, makes it a list
        (separated by semicolon or comma), and appends element from list
        into database of known values for given tag if that value hasn't
        been encountered earlier.
        This way we can be sure that known values in database are unique
        """
        if name == "author":
            name = "authors"

        if ";" in values:
            values = values.split(";")
        else:
            values = values.split(",")

        known_values = getattr(self, name)

        # TODO: I guess we don't support empty values? pelican does this a bit different
        values = [v.strip() for v in values]

        for v in values:
            if v and v not in known_values:
                logging.debug("Appending {v} to {n}".format(v=v, n=name))
                known_values.append(v)
                setattr(self, name, known_values)
