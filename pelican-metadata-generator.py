#!/usr/bin/env python3

import sys
import logging
from PyQt5 import (QtCore, QtWidgets)

import PMGModel
import PMGView
import PMGController


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.ERROR)
    file_format = 'markdown'
    path = None
    if len(sys.argv) > 1:
        path = sys.argv[1]

    known_metadata_model = PMGModel.MetadataDatabase()

    app = QtWidgets.QApplication(sys.argv)
    post_model = PMGModel.NewPostMetadata()
    window = PMGView.MainWindow()
    controller = PMGController.Controller(known_metadata_model, post_model, window)

    known_metadata_model.read_directory(path)

    # FIXME: be in view?
    for file_format_action in window.choose_file_format_group.actions():
        if file_format_action.text().lower() == file_format:
            file_format_action.setChecked(True)
    window.setupTab.dateField.setDateTime(QtCore.QDateTime.currentDateTime())
    window.show()

    sys.exit(app.exec_())
