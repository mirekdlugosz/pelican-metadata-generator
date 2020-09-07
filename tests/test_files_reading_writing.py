import unittest

import os
import io
import logging

from pelican_metadata_generator import file_handler


CUR_DIR = os.path.dirname(__file__)
CONTENT_PATH = os.path.join(CUR_DIR, "posts")


class TestPostFile(unittest.TestCase):
    def test_extension_md_is_markdown(self):
        post = file_handler.Factory(
            os.path.join(CONTENT_PATH, "file_that_doesnt_exist.md")
        ).generate()

        self.assertIsInstance(post, file_handler.MarkdownHandler)

    def test_extension_markdown_is_markdown(self):
        post = file_handler.Factory(
            os.path.join(CONTENT_PATH, "file_that_doesnt_exist.markdown")
        ).generate()

        self.assertIsInstance(post, file_handler.MarkdownHandler)

    def test_extension_mdown_is_markdown(self):
        post = file_handler.Factory(
            os.path.join(CONTENT_PATH, "file_that_doesnt_exist.mdown")
        ).generate()

        self.assertIsInstance(post, file_handler.MarkdownHandler)

    def test_extension_mkd_is_markdown(self):
        post = file_handler.Factory(
            os.path.join(CONTENT_PATH, "file_that_doesnt_exist.mkd")
        ).generate()

        self.assertIsInstance(post, file_handler.MarkdownHandler)

    def test_force_markdown_format_on_file_without_extension(self):
        post = file_handler.Factory(
            os.path.join(CONTENT_PATH, "file_that_doesnt_exist"), "markdown"
        ).generate()

        self.assertIsInstance(post, file_handler.MarkdownHandler)

    def test_force_markdown_format_on_file_with_other_extension(self):
        post = file_handler.Factory(
            os.path.join(CONTENT_PATH, "file_that_doesnt_exist.rst"), "markdown"
        ).generate()

        self.assertIsInstance(post, file_handler.MarkdownHandler)


class TestMarkdownHandler(unittest.TestCase):
    def test_read_nonexisting_file(self):
        expected_headers = {}
        expected_content = ""
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_that_doesnt_exist.md"))

        self.assertFalse(md.exists)
        self.assertEqual(md.headers, expected_headers)
        self.assertEqual(md.post_content, expected_content)

    def test_directory_is_treated_as_non_existing_file(self):
        expected_headers = {}
        expected_content = ""
        md = file_handler.MarkdownHandler(CONTENT_PATH)

        self.assertFalse(md.exists)
        self.assertEqual(md.headers, expected_headers)
        self.assertEqual(md.post_content, expected_content)

    def test_read_file_without_metadata(self):
        expected_headers = {}
        expected_content = "File without headers\n"
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_without_headers.md"))

        self.assertTrue(md.exists)
        self.assertEqual(md.headers, expected_headers)
        self.assertEqual(md.post_content, expected_content)

    def test_read_long_file_without_metadata(self):
        expected_headers = {}
        expected_content = (
            "\n\n"
            "                    GNU AFFERO GENERAL PUBLIC LICENSE\n"
            "                       Version 3, 19 November 2007\n"
            "\n"
            " Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>\n"
            " Everyone is permitted to copy and distribute verbatim copies\n"
            " of this license document, but changing it is not allowed.\n"
            "\n"
        )
        md = file_handler.MarkdownHandler(
            os.path.join(CONTENT_PATH, "long_file_with_blank_lines_at_top.md")
        )

        self.assertTrue(md.exists)
        self.assertEqual(md.headers, expected_headers)
        self.assertEqual(md.post_content, expected_content)
        self.assertEqual(md.raw_content, "\n" + expected_content)

    def test_read_file_with_metadata(self):
        expected_headers = {
            "title": "File with headers",
            "slug": "file-with-headers",
            "category": "Markdown",
            "tags": "File, Tag, Testing",
        }
        expected_content = "File with headers\n"
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_with_headers.md"))

        self.assertTrue(md.exists)
        self.assertEqual(md.headers, expected_headers)
        self.assertEqual(md.post_content, expected_content)

    def test_read_file_with_metadata_after_text(self):
        expected_headers = {
            "title": "File with metadata in text",
        }
        expected_content = (
            "This is example file with metadata-like line after paragraph of text\n"
            "Slug: file-with-metadata-in-text\n"
            "And one more paragraph\n"
        )
        md = file_handler.MarkdownHandler(
            os.path.join(CONTENT_PATH, "file_with_headers_after_text.md")
        )

        self.assertTrue(md.exists)
        self.assertEqual(md.headers, expected_headers)
        self.assertEqual(md.post_content, expected_content)

    def test_read_file_with_multiline_metadata(self):
        expected_headers = {
            "title": "File with headers",
            "category": "Markdown",
            "tags": "File; Tag; Testing",
        }
        expected_content = ""
        md = file_handler.MarkdownHandler(
            os.path.join(CONTENT_PATH, "file_with_multiline_metadata.md")
        )

        self.assertTrue(md.exists)
        self.assertEqual(md.headers, expected_headers)
        self.assertEqual(md.post_content, expected_content)

    def test_read_file_with_YAML_headers(self):
        filepath = os.path.join(CONTENT_PATH, "file_with_YAML_headers.md")
        with open(filepath) as fh:
            expected_raw_content = fh.read()
        expected_headers = {
            "title": "File with YAML headers",
            "slug": "file-with-yaml-headers",
            "category": "Markdown",
        }
        expected_content = "This file has YAML-style headers\n"
        md = file_handler.MarkdownHandler(filepath)

        self.assertTrue(md.exists)
        self.assertEqual(md.headers, expected_headers)
        self.assertEqual(md.post_content, expected_content)
        self.assertEqual(md.raw_content, expected_raw_content)

    def test_read_file_without_separator_between_headers_and_content(self):
        expected_headers = {
            "title": "File without separator after headers",
            "category": "Markdown",
        }
        expected_content = "This file has no separator between headers and content\n"
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_without_separator.md"))

        self.assertTrue(md.exists)
        self.assertEqual(md.headers, expected_headers)
        self.assertEqual(md.post_content, expected_content)

    def test_read_file_with_url_in_first_line_without_separator(self):
        expected_headers = {
            "title": "URL below headers",
        }
        expected_content = "http://miroslaw-zalewski.eu/\n"
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "url_in_first_line.md"))

        self.assertTrue(md.exists)
        self.assertEqual(md.headers, expected_headers)
        self.assertEqual(md.post_content, expected_content)

    def test_read_colon_after_separator(self):
        expected_headers = {
            "title": "File with colon in first line",
            "category": "Markdown",
        }
        expected_content = "Test: This is normal text, not header\n"
        md = file_handler.MarkdownHandler(
            os.path.join(CONTENT_PATH, "file_with_colon_in_first_line.md")
        )

        self.assertTrue(md.exists)
        self.assertEqual(md.headers, expected_headers)
        self.assertEqual(md.post_content, expected_content)

    def test_generate_headers_without_title(self):
        expected = "Slug: without-headers\n" "Date: 2017-02-01 12:00"
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_that_doesnt_exist.md"))
        md.headers = {
            "slug": "without-headers",
            "date": "2017-02-01 12:00",
        }

        self.assertEqual(md.formatted_headers, expected)

    def test_generate_headers_order(self):
        expected = (
            "Title: Predictable order\n"
            "Slug: predictable-order\n"
            "Date: 2017-02-01 12:00\n"
            "Modified: 2017-02-01 12:01\n"
            "Category: Markdown\n"
            "Tags: Headers, Markdown\n"
            "Authors: Mirosław Zalewski\n"
            "Summary: Headers are written in predictable order"
        )
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_that_doesnt_exist.md"))
        md.headers = {
            "modified": "2017-02-01 12:01",
            "summary": "Headers are written in predictable order",
            "category": "Markdown",
            "title": "Predictable order",
            "tags": "Headers, Markdown",
            "slug": "predictable-order",
            "authors": "Mirosław Zalewski",
            "date": "2017-02-01 12:00",
        }

        self.assertEqual(md.formatted_headers, expected)

    def test_prepend_headers_non_existing_file(self):
        expected = (
            "Title: Sample title\n"
            "Slug: sample-title\n"
            "Date: 2017-02-01 12:00\n"
            "Category: Test category\n"
            "Tags: Another, Tag\n"
            "\n"
        )
        test_stream = io.StringIO()
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_that_doesnt_exist.md"))
        md.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        md.prepend_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_overwrite_headers_non_existing_file(self):
        expected = (
            "Title: Sample title\n"
            "Slug: sample-title\n"
            "Date: 2017-02-01 12:00\n"
            "Category: Test category\n"
            "Tags: Another, Tag\n"
            "\n"
        )
        test_stream = io.StringIO()
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_that_doesnt_exist.md"))
        md.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        md.overwrite_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_prepend_headers_file_without_headers(self):
        expected = (
            "Title: Sample title\n"
            "Slug: sample-title\n"
            "Date: 2017-02-01 12:00\n"
            "Category: Test category\n"
            "Tags: Another, Tag\n"
            "\n"
            "File without headers\n"
        )
        test_stream = io.StringIO()
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_without_headers.md"))
        md.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        md.prepend_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_overwrite_headers_file_without_headers(self):
        expected = (
            "Title: Sample title\n"
            "Slug: sample-title\n"
            "Date: 2017-02-01 12:00\n"
            "Category: Test category\n"
            "Tags: Another, Tag\n"
            "\n"
            "File without headers\n"
        )
        test_stream = io.StringIO()
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_without_headers.md"))
        md.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        md.overwrite_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_prepend_headers_file_with_headers(self):
        expected = (
            "Title: Sample title\n"
            "Slug: sample-title\n"
            "Date: 2017-02-01 12:00\n"
            "Category: Test category\n"
            "Tags: Another, Tag\n"
            "\n"
            "Title: File with headers\n"
            "Slug: file-with-headers\n"
            "Category: Markdown\n"
            "Tags: File, Tag, Testing\n"
            "\n"
            "File with headers\n"
        )
        test_stream = io.StringIO()
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_with_headers.md"))
        md.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        md.prepend_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_overwrite_headers_file_with_headers(self):
        expected = (
            "Title: Sample title\n"
            "Slug: sample-title\n"
            "Date: 2017-02-01 12:00\n"
            "Category: Test category\n"
            "Tags: Another, Tag\n"
            "\n"
            "File with headers\n"
        )
        test_stream = io.StringIO()
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_with_headers.md"))
        md.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        md.overwrite_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_prepend_headers_restructuredtext_file(self):
        expected = (
            "Title: Sample title\n"
            "Slug: sample-title\n"
            "Date: 2017-02-01 12:00\n"
            "Category: Test category\n"
            "Tags: Another, Tag\n"
            "\n"
            "File with headers\n"
            "#################\n"
            "\n"
            ":slug: file-with-headers\n"
            ":category: ReStructuredText\n"
            ":tags: File, Tag, Testing\n"
            "\n"
            "File with headers\n"
        )
        test_stream = io.StringIO()
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_with_headers.rst"))
        md.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        md.prepend_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_overwrite_headers_restructuredtext_file(self):
        expected = (
            "Title: Sample title\n"
            "Slug: sample-title\n"
            "Date: 2017-02-01 12:00\n"
            "Category: Test category\n"
            "Tags: Another, Tag\n"
            "\n"
            "File with headers\n"
            "#################\n"
            "\n"
            ":slug: file-with-headers\n"
            ":category: ReStructuredText\n"
            ":tags: File, Tag, Testing\n"
            "\n"
            "File with headers\n"
        )
        test_stream = io.StringIO()
        md = file_handler.MarkdownHandler(os.path.join(CONTENT_PATH, "file_with_headers.rst"))
        md.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        md.overwrite_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)


class TestRestructuredtextHandler(unittest.TestCase):
    def test_read_nonexisting_file(self):
        expected_headers = {}
        expected_content = ""
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_that_doesnt_exist.rst")
        )

        self.assertFalse(rst.exists)
        self.assertEqual(rst.headers, expected_headers)
        self.assertEqual(rst.post_content, expected_content)

    def test_directory_is_treated_as_non_existing_file(self):
        expected_headers = {}
        expected_content = ""
        rst = file_handler.RestructuredtextHandler(CONTENT_PATH)

        self.assertFalse(rst.exists)
        self.assertEqual(rst.headers, expected_headers)
        self.assertEqual(rst.post_content, expected_content)

    def test_read_file_without_metadata(self):
        expected_headers = {}
        expected_content = "File without headers\n"
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_without_headers.rst")
        )

        self.assertTrue(rst.exists)
        self.assertEqual(rst.headers, expected_headers)
        self.assertEqual(rst.post_content, expected_content)

    def test_read_long_file_without_metadata(self):
        expected_headers = {}
        expected_content = (
            "                    GNU AFFERO GENERAL PUBLIC LICENSE\n"
            "                       Version 3, 19 November 2007\n"
            "\n"
            " Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>\n"
            " Everyone is permitted to copy and distribute verbatim copies\n"
            " of this license document, but changing it is not allowed.\n"
            "\n"
        )
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "long_file_with_blank_lines_at_top.rst")
        )

        self.assertTrue(rst.exists)
        self.assertEqual(rst.headers, expected_headers)
        self.assertEqual(rst.post_content, expected_content)
        self.assertEqual(rst.raw_content, "\n\n\n" + expected_content)

    def test_read_file_with_metadata(self):
        expected_headers = {
            "title": "File with headers",
            "slug": "file-with-headers",
            "category": "ReStructuredText",
            "tags": "File, Tag, Testing",
        }
        expected_content = "File with headers\n"
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_with_headers.rst")
        )

        self.assertTrue(rst.exists)
        self.assertEqual(rst.headers, expected_headers)
        self.assertEqual(rst.post_content, expected_content)

    def test_read_file_with_metadata_after_text(self):
        expected_headers = {
            "title": "File with metadata in text",
        }
        expected_content = (
            "This is example file with metadata-like line after paragraph of text\n"
            ":slug: file-with-metadata-in-text\n"
            "And one more paragraph\n"
        )
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_with_headers_after_text.rst")
        )

        self.assertTrue(rst.exists)
        self.assertEqual(rst.headers, expected_headers)
        self.assertEqual(rst.post_content, expected_content)

    def test_read_file_with_metadata_right_after_title(self):
        expected_headers = {
            "title": "File with metadata right after title",
            "category": "ReStructuredText",
        }
        expected_content = "Sample paragraph\n"
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_with_headers_right_after_title.rst")
        )

        self.assertTrue(rst.exists)
        self.assertEqual(rst.headers, expected_headers)
        self.assertEqual(rst.post_content, expected_content)

    def test_read_file_with_multiline_metadata(self):
        expected_headers = {
            "title": "File with headers",
            "category": "ReStructuredText",
            "summary": "This is long summary that takes multiple lines as input",
        }
        expected_content = ""
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_with_multiline_metadata.rst")
        )

        self.assertTrue(rst.exists)
        self.assertEqual(rst.headers, expected_headers)
        self.assertEqual(rst.post_content, expected_content)

    def test_read_file_with_list_metadata(self):
        expected_headers = {
            "title": "File with headers",
            "category": "ReStructuredText",
            "authors": "Author, First; Author, Second",
        }
        expected_content = ""
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_with_list_metadata.rst")
        )

        self.assertTrue(rst.exists)
        self.assertEqual(rst.headers, expected_headers)
        self.assertEqual(rst.post_content, expected_content)

    def test_read_file_with_title_only(self):
        expected_headers = {
            "title": "File with title only",
        }
        expected_content = "This file has title, but no other metadata\n"
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_with_title_only.rst")
        )

        self.assertTrue(rst.exists)
        self.assertEqual(rst.headers, expected_headers)
        self.assertEqual(rst.post_content, expected_content)

    def test_read_paragraph_starting_with_colon_after_separator(self):
        expected_headers = {
            "title": "File with colon in first line",
            "category": "ReStructuredText",
        }
        expected_content = ":test: This is normal text, not header\n"
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_with_colon_in_first_line.rst")
        )

        self.assertTrue(rst.exists)
        self.assertEqual(rst.headers, expected_headers)
        self.assertEqual(rst.post_content, expected_content)

    def test_generate_headers_without_title(self):
        expected = ":slug: without-headers\n" ":date: 2017-02-01 12:00"
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_that_doesnt_exist.rst")
        )
        rst.headers = {
            "slug": "without-headers",
            "date": "2017-02-01 12:00",
        }

        self.assertEqual(rst.formatted_headers, expected)

    def test_generate_headers_order(self):
        expected = (
            "Predictable order\n"
            "#################\n"
            "\n"
            ":slug: predictable-order\n"
            ":date: 2017-02-01 12:00\n"
            ":modified: 2017-02-01 12:01\n"
            ":category: Markdown\n"
            ":tags: Headers, Markdown\n"
            ":authors: Mirosław Zalewski\n"
            ":summary: Headers are written in predictable order"
        )
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_that_doesnt_exist.rst")
        )
        rst.headers = {
            "modified": "2017-02-01 12:01",
            "summary": "Headers are written in predictable order",
            "category": "Markdown",
            "title": "Predictable order",
            "tags": "Headers, Markdown",
            "slug": "predictable-order",
            "authors": "Mirosław Zalewski",
            "date": "2017-02-01 12:00",
        }

        self.assertEqual(rst.formatted_headers, expected)

    def test_prepend_headers_non_existing_file(self):
        expected = (
            "Sample title\n"
            "############\n"
            "\n"
            ":slug: sample-title\n"
            ":date: 2017-02-01 12:00\n"
            ":category: Test category\n"
            ":tags: Another, Tag\n"
            "\n"
        )
        test_stream = io.StringIO()
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_that_doesnt_exist.rst")
        )
        rst.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        rst.prepend_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_overwrite_headers_non_existing_file(self):
        expected = (
            "Sample title\n"
            "############\n"
            "\n"
            ":slug: sample-title\n"
            ":date: 2017-02-01 12:00\n"
            ":category: Test category\n"
            ":tags: Another, Tag\n"
            "\n"
        )
        test_stream = io.StringIO()
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_that_doesnt_exist.rst")
        )
        rst.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        rst.overwrite_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_prepend_headers_file_without_headers(self):
        expected = (
            "Sample title\n"
            "############\n"
            "\n"
            ":slug: sample-title\n"
            ":date: 2017-02-01 12:00\n"
            ":category: Test category\n"
            ":tags: Another, Tag\n"
            "\n"
            "File without headers\n"
        )
        test_stream = io.StringIO()
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_without_headers.rst")
        )
        rst.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        rst.prepend_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_overwrite_headers_file_without_headers(self):
        expected = (
            "Sample title\n"
            "############\n"
            "\n"
            ":slug: sample-title\n"
            ":date: 2017-02-01 12:00\n"
            ":category: Test category\n"
            ":tags: Another, Tag\n"
            "\n"
            "File without headers\n"
        )
        test_stream = io.StringIO()
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_without_headers.rst")
        )
        rst.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        rst.overwrite_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_prepend_headers_file_with_headers(self):
        expected = (
            "Sample title\n"
            "############\n"
            "\n"
            ":slug: sample-title\n"
            ":date: 2017-02-01 12:00\n"
            ":category: Test category\n"
            ":tags: Another, Tag\n"
            "\n"
            "File with headers\n"
            "#################\n"
            "\n"
            ":slug: file-with-headers\n"
            ":category: ReStructuredText\n"
            ":tags: File, Tag, Testing\n"
            "\n"
            "File with headers\n"
        )
        test_stream = io.StringIO()
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_with_headers.rst")
        )
        rst.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        rst.prepend_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_overwrite_headers_file_with_headers(self):
        expected = (
            "Sample title\n"
            "############\n"
            "\n"
            ":slug: sample-title\n"
            ":date: 2017-02-01 12:00\n"
            ":category: Test category\n"
            ":tags: Another, Tag\n"
            "\n"
            "File with headers\n"
        )
        test_stream = io.StringIO()
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_with_headers.rst")
        )
        rst.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        rst.overwrite_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_prepend_headers_markdown_file(self):
        expected = (
            "Sample title\n"
            "############\n"
            "\n"
            ":slug: sample-title\n"
            ":date: 2017-02-01 12:00\n"
            ":category: Test category\n"
            ":tags: Another, Tag\n"
            "\n"
            "Title: File with headers\n"
            "Slug: file-with-headers\n"
            "Category: Markdown\n"
            "Tags: File, Tag, Testing\n"
            "\n"
            "File with headers\n"
        )
        test_stream = io.StringIO()
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_with_headers.md")
        )
        rst.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        rst.prepend_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)

    def test_overwrite_headers_markdown_file(self):
        expected = (
            "Sample title\n"
            "############\n"
            "\n"
            ":slug: sample-title\n"
            ":date: 2017-02-01 12:00\n"
            ":category: Test category\n"
            ":tags: Another, Tag\n"
            "\n"
            "Title: File with headers\n"
            "Slug: file-with-headers\n"
            "Category: Markdown\n"
            "Tags: File, Tag, Testing\n"
            "\n"
            "File with headers\n"
        )
        test_stream = io.StringIO()
        rst = file_handler.RestructuredtextHandler(
            os.path.join(CONTENT_PATH, "file_with_headers.md")
        )
        rst.headers = {
            "title": "Sample title",
            "slug": "sample-title",
            "date": "2017-02-01 12:00",
            "category": "Test category",
            "tags": "Another, Tag",
        }
        rst.overwrite_headers_stream(test_stream)

        test_stream.seek(0)

        self.assertEqual(test_stream.read(), expected)
