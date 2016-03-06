#!/usr/bin/env python3

import os
import sys
import logging

from PyQt5.QtCore import (Qt, QObject, QDateTime, pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QWidget,
        QTabWidget, QButtonGroup,
        QHBoxLayout, QVBoxLayout, QFormLayout, QGridLayout, 
        QCheckBox, QPlainTextEdit, QLineEdit, QComboBox, 
        QDateTimeEdit, QPushButton)

import view
import model

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.ERROR)

class PelicanMetadata():
    def __init__(self, path=None):
        self.category = []
        self.tags = []
        self.authors = []

        if path:
            path = os.path.abspath(path)
            if (os.path.isdir(path)):
                self._readPathFiles(path)

    def _readPathFiles(self, path):
        for root, dirs, files in os.walk(path):
            for filename in files:
                self._parseFile(os.path.join(root, filename))

    def _parseFile(self, path):
        logging.debug("Processing {file}".format(file=path))

        p, ext = os.path.splitext(path)
        if ext not in ['.md', '.markdown', '.mdown', '.mkd']:
            msg = "Ignoring {file} because it has unsupported extension: {extension}"
            logging.info(msg.format(file=path, extension=ext))
            return

        with open(path, 'r') as f:
            content = f.readlines()

        for line in content:
            kv = line.split(':')
            if len(kv) != 2:
                continue

            name, value = kv[0].lower(), kv[1].strip()
            # Feeble attempt to skip lines that aren't real metadata
            if " " in name or "http" in name:
                continue
            logging.debug("Metadata {name}: {value}".format(name=name, value=value))

            if name in ['tags', 'category', 'author', 'authors']:
                self._appendMeta(name, value)

    def _appendMeta(self, name, values):
        """
        This takes string that is metadata tag value, makes it a list 
        (separated by semicolon or comma), and appends element from list
        into database of known values for given tag if that value hasn't
        been encountered earlier.
        This way we can be sure that known values in database are unique
        """
        if name == 'author':
            name = 'authors'

        if ';' in values:
            values = values.split(';')
        else:
            values = values.split(',')

        # TODO: I guess we don't support empty values? pelican does this a bit different
        values = [v.strip() for v in values]

        known_values = getattr(self, name)

        for v in values:
            if v and v not in known_values:
                logging.debug("Appending {v} to {n}".format(v=v, n=name))
                known_values.append(v)
                setattr(self, name, known_values)

if __name__ == '__main__':
    path = None
    if len(sys.argv) > 1:
        path = sys.argv[1]

    known_metadata = PelicanMetadata(path)

    app = QApplication(sys.argv)
    window = view.Window()
    data = model.MetadataModel()
    data.changed.connect(window.generatedTab.generateContent)
    window.setupTab.dateField.setDateTime(QDateTime.currentDateTime())
    window.show()
    sys.exit(app.exec_())
