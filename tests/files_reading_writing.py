import unittest

import os
import io
import logging

import FileHandler

CUR_DIR = os.path.dirname(__file__)
CONTENT_PATH = os.path.join(CUR_DIR, 'posts')

class TestReadingFiles(unittest.TestCase):

    def test_read_nonexisting_file(self):
        pass

    def test_read_file_without_metadata(self):
        pass

    def test_read_file_with_metadata(self):
        pass

    def test_read_tags(self):
        pass

    def test_read_category(self):
        pass

    def test_read_authors(self):
        pass

    def test_read_author(self):
        pass

class TestWritingHeaders(unittest.TestCase):

    def test_prepend_headers(self):
        expected = (
                "Title: Sample title\n"
                "Slug: sample-title\n"
                "Date: 2017-02-01 12:00\n"
                "Category: Test category\n"
                "Tags: Another, Tag\n"
                "\n"
                "Test\n"
            )
        test_stream = io.StringIO()
        md = FileHandler.MarkdownHandler(os.path.join(CONTENT_PATH , "test.md"))
        md.read()
        md.headers = {
                "title": "Sample title",
                "slug": "sample-title",
                "date": "2017-02-01 12:00",
                "category": "Test category",
                "tags": ["Another", "Tag"],
            }
        md.prepend_headers_stream(test_stream)
        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_overwrite_headers(self):
        pass

    def test_create_new_file(self):
        pass
