from PyQt5 import (QtCore, QtWidgets)


class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.setupTab = SetupTab()
        self.generatedTab = GeneratedTab()

        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(self.setupTab, "Metadata form")
        tabWidget.addTab(self.generatedTab, "Generated metadata")

        self.saveAsFileButton = QtWidgets.QPushButton("Save as file")

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(tabWidget)
        mainLayout.addWidget(self.saveAsFileButton)
        self.setLayout(mainLayout)

        self.setWindowTitle("Pelican Metadata Generator")

        self.saveAsFileButton.setAutoDefault(False)
        self.saveFileDialog = QtWidgets.QFileDialog()
        self.saveFileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)

    def showSaveDialog(self, filename):
        self.saveFileDialog.selectFile(filename)
        self.saveFileDialog.exec()

class SetupTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SetupTab, self).__init__(parent)

        self.titleField = QtWidgets.QLineEdit()

        self.slugActive = QtWidgets.QCheckBox("")
        self.slugField = QtWidgets.QLineEdit()
        self.slugLine = QtWidgets.QHBoxLayout()
        self.slugLine.addWidget(self.slugActive)
        self.slugLine.addWidget(self.slugField)
        self.slugActive.setToolTip("Generate automatically")
        self.slugActive.stateChanged.connect(self.slugField.setReadOnly)
        self.slugActive.setChecked(True)

        self.dateField = QtWidgets.QDateTimeEdit()
        self.dateField.setCalendarPopup(True)

        self.modifiedActive = QtWidgets.QCheckBox("")
        self.modifiedField = QtWidgets.QDateTimeEdit()
        self.modifiedLine = QtWidgets.QHBoxLayout()
        self.modifiedLine.addWidget(self.modifiedActive)
        self.modifiedLine.addWidget(self.modifiedField)
        self.modifiedActive.setToolTip("Include in output")
        self.modifiedActive.stateChanged.connect(self._setModifiedAllowed)
        self.modifiedField.setCalendarPopup(True)
        self.modifiedField.setDateTime(QtCore.QDateTime.currentDateTime())
        self._setModifiedAllowed(False)

        self.categoryList = QtWidgets.QComboBox()
        self.categoryField = QtWidgets.QLineEdit()
        self.categoryLine = QtWidgets.QHBoxLayout()
        self.categoryLine.addWidget(self.categoryList)
        self.categoryLine.addWidget(self.categoryField)
        self.categoryList.addItem("Pick value")

        self.tagButtonsLayout = QtWidgets.QGridLayout()
        self.tagButtonsGroup = QtWidgets.QButtonGroup()
        self.tagButtonsGroup.setExclusive(False)
        self.tagField = QtWidgets.QLineEdit()
        self.tagLine = QtWidgets.QVBoxLayout()
        self.tagLine.addLayout(self.tagButtonsLayout)
        self.tagLine.addWidget(self.tagField)

        self.authorList = QtWidgets.QComboBox()
        self.authorField = QtWidgets.QLineEdit()
        self.authorLine = QtWidgets.QHBoxLayout()
        self.authorLine.addWidget(self.authorList)
        self.authorLine.addWidget(self.authorField)
        self.authorList.addItem("Pick value")

        self.summaryField = QtWidgets.QPlainTextEdit()
        self.summaryField.setMaximumHeight(36)

        mainLayout = QtWidgets.QFormLayout()
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

        button = QtWidgets.QPushButton(tag)
        self.tagButtonsGroup.addButton(button)
        button.setAutoDefault(False)
        button.setCheckable(True)
        button.setChecked(selected)
        i = self.tagButtonsLayout.count()
        inRow = 4
        self.tagButtonsLayout.addWidget(button, i / inRow, i % inRow)

class GeneratedTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GeneratedTab, self).__init__(parent)

        self.generatedField = QtWidgets.QPlainTextEdit()

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.generatedField)
        self.setLayout(mainLayout)

    def set_content(self, text):
        self.generatedField.setPlainText(text)
