#!/usr/bin/env python3

import sys
import logging
import argparse
from PyQt5 import (QtCore, QtWidgets)

import PMGModel
import PMGView
import PMGController


def process_args():
    description = "Generate Pelican post metadata based on previous content"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--format', '-f', help="Output file format",
                        choices=["markdown", "restructuredtext"],
                        default="markdown")
    parser.add_argument('--debug', '-v', help="Be more verbose; may be passed up to 5 times",
            action="count")
    parser.add_argument('--directory', '-d', help="Directories to read metadata from",
            nargs='*', default=[])

    return parser.parse_known_args()


if __name__ == '__main__':
    args, unparsed_args = process_args()

    # Logging
    debug_level = logging.CRITICAL
    debug_levels = ["", logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]

    if args.debug:
        if args.debug >= len(debug_levels):
            args.debug = len(debug_levels) - 1
        debug_level = debug_levels[args.debug]

    logging.basicConfig(format='%(asctime)s %(message)s', level=debug_level)

    # File format
    file_format = args.format

    # Initialize main objects
    app = QtWidgets.QApplication(unparsed_args)
    known_metadata_model = PMGModel.MetadataDatabase()
    post_model = PMGModel.NewPostMetadata()
    window = PMGView.MainWindow()
    controller = PMGController.Controller(known_metadata_model, post_model, window)

    # Load data from source directories
    for directory in args.directory:
        known_metadata_model.read_directory(directory)

    # Set model and view in expected state
    post_model.file_format = file_format
    for file_format_action in window.choose_file_format_group.actions():
        if file_format_action.text().lower() == file_format:
            file_format_action.setChecked(True)
    window.setupTab.dateField.setDateTime(QtCore.QDateTime.currentDateTime())
    window.show()

    sys.exit(app.exec_())
