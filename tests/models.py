import unittest

import os
import io
import logging

import PMGModel


CUR_DIR = os.path.dirname(__file__)
CONTENT_PATH = os.path.join(CUR_DIR, 'posts')

class TestPostMetadata(unittest.TestCase):

    def setUp(self):
        self.post_metadata = PMGModel.NewPostMetadata()

    def test_tags_formatting(self):
        expected = "Another, Tag"

        self.post_metadata.tags = ["Tag", "Another"]
        headers = self.post_metadata._format_headers_object()

        self.assertEqual(headers["tags"], expected)

    def test_empty_string_is_skipped(self):
        headers = self.post_metadata._format_headers_object()

        self.assertNotIn("modified", headers)

class TestMetadataDatabase(unittest.TestCase):

    def setUp(self):
        self.db = PMGModel.MetadataDatabase()

    def test_read_tags_separated_by_commas(self):
        expected = ["First", "Tag"]

        self.db._parseFile(os.path.join(CONTENT_PATH , "tags_separated_by_comma.md"))

        self.assertEqual(self.db.tags, expected)

    def test_read_tags_separated_by_semicolons(self):
        expected = ["First", "Tag"]

        self.db._parseFile(os.path.join(CONTENT_PATH , "tags_separated_by_semicolon.md"))

        self.assertEqual(self.db.tags, expected)

    def test_reading_files_with_different_categories(self):
        expected = ["Tags testing", "Markdown"]

        self.db._parseFile(os.path.join(CONTENT_PATH , "tags_separated_by_comma.md"))
        self.db._parseFile(os.path.join(CONTENT_PATH , "file_with_headers.md"))

        self.assertEqual(self.db.category, expected)

    def test_reading_files_with_the_same_categories(self):
        expected = ["Tags testing"]

        self.db._parseFile(os.path.join(CONTENT_PATH , "tags_separated_by_semicolon.md"))
        self.db._parseFile(os.path.join(CONTENT_PATH , "tags_separated_by_comma.md"))

        self.assertEqual(self.db.category, expected)

    def test_reading_files_with_intersection_of_tags(self):
        expected = ["First", "Tag", "File", "Testing"]

        self.db._parseFile(os.path.join(CONTENT_PATH , "tags_separated_by_comma.md"))
        self.db._parseFile(os.path.join(CONTENT_PATH , "file_with_headers.md"))

        self.assertEqual(self.db.tags, expected)

    def test_reading_file_with_author_field(self):
        expected = ["Mirosław Zalewski"]

        self.db._parseFile(os.path.join(CONTENT_PATH , "author_field.md"))

        self.assertEqual(self.db.authors, expected)

    def test_reading_file_with_authors_field(self):
        expected = ["Mirosław Zalewski"]

        self.db._parseFile(os.path.join(CONTENT_PATH , "authors_field.md"))

        self.assertEqual(self.db.authors, expected)
