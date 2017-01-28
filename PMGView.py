from PyQt5.QtCore import (Qt, QObject, QDateTime, pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QWidget,
        QTabWidget, QButtonGroup,
        QHBoxLayout, QVBoxLayout, QFormLayout, QGridLayout, 
        QCheckBox, QPlainTextEdit, QLineEdit, QComboBox, 
        QDateTimeEdit, QPushButton)

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

        self.saveAsFileButton.setAutoDefault(False)
        self.saveFileDialog = QFileDialog()
        self.saveFileDialog.setAcceptMode(QFileDialog.AcceptSave)

    def showSaveDialog(self, filename):
        self.saveFileDialog.selectFile(filename)
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

        self.tagButtonsLayout = QGridLayout()
        self.tagButtonsGroup = QButtonGroup()
        self.tagButtonsGroup.setExclusive(False)
        self.tagField = QLineEdit()
        self.tagLine = QVBoxLayout()
        self.tagLine.addLayout(self.tagButtonsLayout)
        self.tagLine.addWidget(self.tagField)

        self.authorList = QComboBox()
        self.authorField = QLineEdit()
        self.authorLine = QHBoxLayout()
        self.authorLine.addWidget(self.authorList)
        self.authorLine.addWidget(self.authorField)
        self.authorList.addItem("Pick value")

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

    def set_content(self, text):
        self.generatedField.setPlainText(text)
