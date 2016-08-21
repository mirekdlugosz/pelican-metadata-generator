#!/usr/bin/env python3

import os
import sys
import logging

from slugify import slugify
from PyQt5.QtCore import (Qt, QObject, QDateTime, pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QWidget,
        QTabWidget, QButtonGroup,
        QHBoxLayout, QVBoxLayout, QFormLayout, QGridLayout, 
        QCheckBox, QPlainTextEdit, QLineEdit, QComboBox, 
        QDateTimeEdit, QPushButton)

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.ERROR)

class Window(QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.setupTab = SetupTab()
        self.generatedTab = GeneratedTab()

        tabWidget = QTabWidget()
        tabWidget.addTab(self.setupTab, "Metadata form")
        tabWidget.addTab(self.generatedTab, "Generated metadata")

        self.saveAsFileButton = QPushButton("Save as file")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(tabWidget)
        mainLayout.addWidget(self.saveAsFileButton)
        self.setLayout(mainLayout)

        self.setWindowTitle("Pelican Metadata Generator")

        self.saveAsFileButton.clicked.connect(self.showSaveDialog)
        self.saveAsFileButton.setAutoDefault(False)
        self.saveFileDialog = QFileDialog()
        self.saveFileDialog.setAcceptMode(QFileDialog.AcceptSave)
        if path:
            self.saveFileDialog.setDirectory(path)

    def showSaveDialog(self):
        self.saveFileDialog.selectFile(data.slug + ".md")
        self.saveFileDialog.exec()


class SetupTab(QWidget):
    def __init__(self, parent=None):
        super(SetupTab, self).__init__(parent)

        self.titleField = QLineEdit()

        self.slugActive = QCheckBox("")
        self.slugField = QLineEdit()
        self.slugLine = QHBoxLayout()
        self.slugLine.addWidget(self.slugActive)
        self.slugLine.addWidget(self.slugField)
        self.slugActive.setToolTip("Generate automatically")
        self.slugActive.stateChanged.connect(self.slugField.setReadOnly)
        self.slugActive.setChecked(True)

        self.dateField = QDateTimeEdit()
        self.dateField.setCalendarPopup(True)

        self.modifiedActive = QCheckBox("")
        self.modifiedField = QDateTimeEdit()
        self.modifiedLine = QHBoxLayout()
        self.modifiedLine.addWidget(self.modifiedActive)
        self.modifiedLine.addWidget(self.modifiedField)
        self.modifiedActive.setToolTip("Include in output")
        self.modifiedActive.stateChanged.connect(self._setModifiedAllowed)
        self.modifiedField.setCalendarPopup(True)
        self.modifiedField.setDateTime(QDateTime.currentDateTime())
        self._setModifiedAllowed(False)

        self.categoryList = QComboBox()
        self.categoryField = QLineEdit()
        self.categoryLine = QHBoxLayout()
        self.categoryLine.addWidget(self.categoryList)
        self.categoryLine.addWidget(self.categoryField)
        self.categoryList.addItem("Pick value")
        self.categoryList.addItems(sorted(known_metadata.category, key=str.lower))

        self.tagButtonsLayout = QGridLayout()
        self.tagButtonsGroup = QButtonGroup()
        self.tagButtonsGroup.setExclusive(False)
        self.tagField = QLineEdit()
        self.tagLine = QVBoxLayout()
        self.tagLine.addLayout(self.tagButtonsLayout)
        self.tagLine.addWidget(self.tagField)
        for tag in sorted(known_metadata.tags, key=str.lower):
            self.addTagButton(tag, False)

        self.authorList = QComboBox()
        self.authorField = QLineEdit()
        self.authorLine = QHBoxLayout()
        self.authorLine.addWidget(self.authorList)
        self.authorLine.addWidget(self.authorField)
        self.authorList.addItem("Pick value")
        self.authorList.addItems(sorted(known_metadata.authors, key=str.lower))

        self.summaryField = QPlainTextEdit()
        self.summaryField.setMaximumHeight(36)

        mainLayout = QFormLayout()
        mainLayout.addRow("Title:", self.titleField)
        mainLayout.addRow("Slug:", self.slugLine)
        mainLayout.addRow("Date created:", self.dateField)
        mainLayout.addRow("Date modified:", self.modifiedLine)
        mainLayout.addRow("Category:", self.categoryLine)
        mainLayout.addRow("Tags:", self.tagLine)
        mainLayout.addRow("Author:", self.authorLine)
        mainLayout.addRow("Summary", self.summaryField)
        self.setLayout(mainLayout)

    def _setModifiedAllowed(self, value):
        self.modifiedField.setReadOnly(not value)

    def addTagButton(self, tag, selected=False):
        if selected:
            for i in range(self.tagButtonsLayout.count()):
                button = self.tagButtonsLayout.itemAt(i).widget()
                if button.text() == tag:
                    button.setChecked(True)
                    return

        button = QPushButton(tag)
        self.tagButtonsGroup.addButton(button)
        button.setAutoDefault(False)
        button.setCheckable(True)
        button.setChecked(selected)
        i = self.tagButtonsLayout.count()
        inRow = 4
        self.tagButtonsLayout.addWidget(button, i / inRow, i % inRow)

class GeneratedTab(QWidget):
    def __init__(self, parent=None):
        super(GeneratedTab, self).__init__(parent)

        self.generatedField = QPlainTextEdit()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.generatedField)
        self.setLayout(mainLayout)

    def generateContent(self):
        self.generatedField.setPlainText(data.dumpContent())

class MetadataModel(QObject):
    changed = pyqtSignal()
    def __init__(self):
        super(MetadataModel, self).__init__(None)
        self.title = ""
        self.slug = ""
        self.date = ""
        self.modified = ""
        self.category = ""
        self.tags = []
        self.authors = []
        self.summary = ""
        self._setupConnections()

    def _setupConnections(self):
        window.setupTab.titleField.textChanged.connect(self._titleChanged)
        window.setupTab.slugActive.stateChanged.connect(self._setSlugBasedOnTitle)
        window.setupTab.slugField.textEdited.connect(self._slugChanged)
        window.setupTab.dateField.dateTimeChanged.connect(self._dateChanged)
        window.setupTab.modifiedActive.stateChanged.connect(self._modifiedActiveChanged)
        window.setupTab.modifiedField.dateTimeChanged.connect(self._modifiedChanged)
        window.setupTab.categoryList.currentIndexChanged.connect(self._categoryListChanged)
        window.setupTab.categoryField.textChanged.connect(self._categoryChanged)
        window.setupTab.tagField.returnPressed.connect(self._tagFieldAccepted)
        window.setupTab.tagButtonsGroup.buttonToggled.connect(self._tagButtonToggled)
        window.setupTab.authorList.currentIndexChanged.connect(self._authorListChanged)
        window.setupTab.authorField.textChanged.connect(self._authorChanged)
        window.setupTab.summaryField.textChanged.connect(self._summaryChanged)
        window.saveFileDialog.fileSelected.connect(self._fileSelected)

    def _titleChanged(self, value):
        self._logSignal(self.sender(), [value])
        self.title = value
        self._setSlugBasedOnTitle()
        self.changed.emit()

    def _setSlugBasedOnTitle(self):
        if window.setupTab.slugActive.checkState():
            self._slugChanged(slugify(self.title))
            window.setupTab.slugField.setText(self.slug)

    def _slugChanged(self, value):
        self._logSignal(self.sender(), [value])
        self.slug = value
        self.changed.emit()

    def _dateChanged(self, value):
        value = value.toString("yyyy-MM-dd hh:mm:ss")
        self._logSignal(self.sender(), [value])
        self.date = value
        self.changed.emit()

    def _modifiedActiveChanged(self, value):
        self._logSignal(self.sender(), [str(value)])
        self._modifiedChanged(value)

    def _modifiedChanged(self, value):
        if value:
            self.modified = window.setupTab.modifiedField.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        else:
            self.modified = ""
        self.changed.emit()
    
    def _categoryListChanged(self, value):
        self._logSignal(self.sender(), [str(value)])
        if value == 0:
            value = ""
        else:
            value = window.setupTab.categoryList.itemText(value)
        window.setupTab.categoryField.setText(value)

    def _categoryChanged(self, value):
        self._logSignal(self.sender(), [value])
        self.category = value
        self.changed.emit()

    def _tagFieldAccepted(self):
        values = window.setupTab.tagField.text()
        self._logSignal(self.sender(), [values])
        for v in values.split(','):
            v = v.strip()
            if not v:
                continue
            window.setupTab.addTagButton(v, True)

        window.setupTab.tagField.clear()

    def _tagButtonToggled(self, button, checked):
        value = button.text()
        self._logSignal(self.sender(), [value, str(checked)])
        if checked:
            self.tags.append(value.replace("&", ""))
        else:
            self.tags.remove(value)
        self.changed.emit()

    def _authorListChanged(self, value):
        self._logSignal(self.sender(), [value])
        if value == 0:
            value = ""
        else:
            value = window.setupTab.authorList.itemText(value)
        window.setupTab.authorField.setText(value)

    def _authorChanged(self, value):
        self._logSignal(self.sender(), [value])
        if not value:
            self.authors = []
        else:
            self.authors = [value]
        self.changed.emit()

    def _summaryChanged(self):
        self._logSignal(self.sender(), ["textChanged event"])
        self.summary = window.setupTab.summaryField.toPlainText()
        self.changed.emit()

    def _fileSelected(self, value):
        self._logSignal(self.sender(), [value]) 
        content = self.dumpContent()
        with open(value, 'w') as f:
            f.write(content + "\n")

    def _logSignal(self, caller, values):
        logging.debug("Received {v} from {c}".format(
            v=", ".join(values),
            c=caller))

    def dumpContent(self):
        output = []
        output.append("Title: {t}".format(t=self.title))
        output.append("Slug: {s}".format(s=self.slug))
        output.append("Date: {d}".format(d=self.date))
        if self.modified:
            output.append("Modified: {m}".format(m=self.modified))
        output.append("Category: {c}".format(c=self.category))
        output.append("Tags: {t}".format(t=", ".join(sorted(self.tags, key=str.lower))))
        if self.authors:
            output.append("Authors: {a}".format(a="; ".join(self.authors)))
        if self.summary:
            output.append("Summary: {s}".format(s=self.summary))

        return "\n".join(output)

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
    window = Window()
    data = MetadataModel()
    data.changed.connect(window.generatedTab.generateContent)
    window.setupTab.dateField.setDateTime(QDateTime.currentDateTime())
    window.show()
    sys.exit(app.exec_())
