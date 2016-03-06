from slugify import slugify
from PyQt5.QtCore import (Qt, QObject, QDateTime, pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QWidget,
        QTabWidget, QButtonGroup,
        QHBoxLayout, QVBoxLayout, QFormLayout, QGridLayout, 
        QCheckBox, QPlainTextEdit, QLineEdit, QComboBox, 
        QDateTimeEdit, QPushButton)

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
            self.tags.append(value)
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

