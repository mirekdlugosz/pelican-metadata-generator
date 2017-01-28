#!/usr/bin/env python3

import sys
import logging
from PyQt5 import (QtCore, QtWidgets)

import PMGModel
import PMGView
import PMGController

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.ERROR)
    path = None
    if len(sys.argv) > 1:
        path = sys.argv[1]

    known_metadata_model = PMGModel.MetadataDatabase(path)

    app = QtWidgets.QApplication(sys.argv)
    post_model = PMGModel.NewPostMetadata()
    window = PMGView.Window()
    controller = PMGController.Controller(known_metadata_model, post_model, window)

    # FIXME: be in view?
    window.setupTab.dateField.setDateTime(QtCore.QDateTime.currentDateTime())
    window.show()

    sys.exit(app.exec_())
