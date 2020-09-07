from PyQt5 import QtCore, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    """Builds main application window"""

    prependHeaders = QtCore.pyqtSignal()
    overwriteHeaders = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.app = Window()
        self.setCentralWidget(self.app)
        self.setWindowTitle("Pelican Metadata Generator")

        # FIXME?
        # to retain compatibility with current Controller code
        self.setupTab = self.app.setupTab
        self.generatedTab = self.app.generatedTab
        self.saveAsFileButton = self.app.saveAsFileButton
        self.saveFileDialog = self.app.saveFileDialog

        self.read_metadata_act = QtWidgets.QAction(
            "Read Pelican metadata from directory",
            self,
            shortcut="Ctrl+O",
            triggered=lambda: self.readMetadataDialog.exec(),
        )
        self.quit_act = QtWidgets.QAction("&Quit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.markdown_act = QtWidgets.QAction("Markdown", self, checkable=True)
        self.restructuredtext_act = QtWidgets.QAction("ReStructuredText", self, checkable=True)
        self.choose_file_format_group = QtWidgets.QActionGroup(self)
        self.choose_file_format_group.addAction(self.markdown_act)
        self.choose_file_format_group.addAction(self.restructuredtext_act)

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.read_metadata_act)
        self.choose_file_format_menu = self.fileMenu.addMenu("Output file format")
        for file_format in self.choose_file_format_group.actions():
            self.choose_file_format_menu.addAction(file_format)
        self.fileMenu.addAction(self.quit_act)

        self.readMetadataDialog = QtWidgets.QFileDialog()
        self.readMetadataDialog.setFileMode(QtWidgets.QFileDialog.Directory)
        self.readMetadataDialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)

    def show_file_exists_dialog(self):
        message = """
            <p>Do you want to overwrite headers in selected file?
            <p>Selecting \"No\" will append generated headers at top of file,
            leaving current file content intact.
            If you want to select another file, cancel operation.</p>
            """
        reply = QtWidgets.QMessageBox.question(
            self,
            "Selected file has headers",
            message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.No,
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.overwriteHeaders.emit()
        elif reply == QtWidgets.QMessageBox.No:
            self.prependHeaders.emit()


# FIXME: remove that class entirely
class Window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.setupTab = SetupTab()
        self.generatedTab = GeneratedTab()

        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(self.setupTab, "Metadata form")
        tabWidget.addTab(self.generatedTab, "Generated metadata")

        self.saveAsFileButton = QtWidgets.QPushButton("Save as file")
        self.saveAsFileButton.setShortcut("Ctrl+S")

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(tabWidget)
        mainLayout.addWidget(self.saveAsFileButton)
        self.setLayout(mainLayout)

        self.setWindowTitle("Pelican Metadata Generator")

        self.saveAsFileButton.setAutoDefault(False)
        self.saveFileDialog = QtWidgets.QFileDialog()
        self.saveFileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        self.saveFileDialog.setOption(QtWidgets.QFileDialog.DontConfirmOverwrite, True)

    def showSaveDialog(self, filename):
        self.saveFileDialog.selectFile(filename)
        self.saveFileDialog.exec()


class SetupTab(QtWidgets.QWidget):
    """Builds main tab (with input fields)"""

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

        self.tagButtonsLayout = QtWidgets.QGridLayout()
        self.tagButtonsGroup = QtWidgets.QButtonGroup()
        self.tagButtonsGroup.setExclusive(False)
        tagButtonsScrollArea = QtWidgets.QScrollArea()
        tagButtonsScrollArea.setWidgetResizable(True)
        tagButtonsScrollArea.setMinimumSize(500, 200)  # FIXME: hardcoded values
        tagButtonsScrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        tagButtonsScrollAreaWidget = QtWidgets.QWidget()
        tagButtonsScrollArea.setWidget(tagButtonsScrollAreaWidget)
        tagButtonsScrollAreaWidget.setLayout(self.tagButtonsLayout)
        self.tagField = QtWidgets.QLineEdit()
        self.tagLine = QtWidgets.QVBoxLayout()
        self.tagLine.addWidget(tagButtonsScrollArea)
        self.tagLine.addWidget(self.tagField)

        self.authorList = QtWidgets.QComboBox()
        self.authorField = QtWidgets.QLineEdit()
        self.authorLine = QtWidgets.QHBoxLayout()
        self.authorLine.addWidget(self.authorList)
        self.authorLine.addWidget(self.authorField)

        self.summaryField = QtWidgets.QPlainTextEdit()
        self.summaryField.setMaximumHeight(36)  # FIXME: hardcoded value

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

    def setTagButtons(self, available_tags, checked_tags):
        while True:
            item = self.tagButtonsLayout.itemAt(0)
            if not item:
                break
            self.tagButtonsGroup.removeButton(item.widget())
            self.tagButtonsLayout.removeItem(item)
            item.widget().setParent(None)

        for tag in available_tags:
            button = QtWidgets.QPushButton(tag)
            self.tagButtonsGroup.addButton(button)
            button.setAutoDefault(False)
            button.setCheckable(True)
            button.setChecked(tag in checked_tags)
            i = self.tagButtonsLayout.count()
            inRow = 4  # FIXME: hardcoded value
            self.tagButtonsLayout.addWidget(button, i / inRow, i % inRow)


class GeneratedTab(QtWidgets.QWidget):
    """Builds preview headers tab"""

    def __init__(self, parent=None):
        super(GeneratedTab, self).__init__(parent)

        self.generatedField = QtWidgets.QPlainTextEdit()

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.generatedField)
        self.setLayout(mainLayout)

    def set_content(self, text):
        self.generatedField.setPlainText(text)
