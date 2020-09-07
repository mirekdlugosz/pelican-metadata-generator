from slugify import slugify

from PyQt5 import QtCore


class Controller(QtCore.QObject):
    def __init__(self, known_metadata_model=None, post_model=None, view=None):
        super(Controller, self).__init__(None)
        self.known_metadata_model = known_metadata_model
        self.post_model = post_model
        self.view = view
        self.setup_connections()

    def setup_connections(self):
        self.view.readMetadataDialog.fileSelected.connect(self.known_metadata_model.read_directory)
        self.view.choose_file_format_group.triggered.connect(self._set_file_format)
        self.view.setupTab.titleField.textChanged.connect(self._set_title)
        self.view.setupTab.slugActive.stateChanged.connect(self._set_slug_based_on_title)
        self.view.setupTab.slugField.textEdited.connect(self.post_model.set_slug)
        self.view.setupTab.dateField.dateTimeChanged.connect(self.post_model.set_created_date)
        self.view.setupTab.modifiedActive.stateChanged.connect(self._modified_date_active_changed)
        self.view.setupTab.modifiedField.dateTimeChanged.connect(self.post_model.set_modified_date)
        self.view.setupTab.categoryList.currentIndexChanged.connect(
            self._category_list_item_selected
        )
        self.view.setupTab.categoryField.textChanged.connect(self.post_model.set_category)
        self.view.setupTab.tagButtonsGroup.buttonToggled.connect(self._tag_button_toggled)
        self.view.setupTab.tagField.returnPressed.connect(self._set_tags_group)
        self.view.setupTab.authorList.currentIndexChanged.connect(self._author_list_item_selected)
        self.view.setupTab.authorField.textChanged.connect(self.post_model.set_author)
        self.view.setupTab.summaryField.textChanged.connect(
            lambda: self.post_model.set_summary(self.view.setupTab.summaryField.toPlainText())
        )
        self.view.saveAsFileButton.clicked.connect(
            lambda: self.view.app.showSaveDialog(self.post_model.filename)
        )
        self.view.saveFileDialog.fileSelected.connect(self.post_model.to_file)
        self.view.prependHeaders.connect(self.post_model.to_file_prepend_headers)
        self.view.overwriteHeaders.connect(self.post_model.to_file_overwrite_headers)
        self.post_model.fileHasHeaders.connect(self.view.show_file_exists_dialog)
        self.post_model.changed.connect(
            lambda: self.view.generatedTab.set_content(self.post_model.as_pelican_header())
        )
        self.known_metadata_model.changed.connect(self._update_view_options_based_on_metadata)

    def _set_file_format(self, value):
        self.post_model.set_file_format(value.text().lower().replace("&", ""))

    def _set_title(self, value):
        self.post_model.set_title(value)
        self._set_slug_based_on_title()

    def _set_slug_based_on_title(self):
        if self.view.setupTab.slugActive.isChecked():
            self.post_model.set_slug(slugify(self.post_model.title))
            self.view.setupTab.slugField.setText(self.post_model.slug)

    def _modified_date_active_changed(self, state):
        if not state:
            self.post_model.set_modified_date(None)

    def _category_list_item_selected(self, value):
        if value == 0:
            value = ""
        else:
            value = self.view.setupTab.categoryList.itemText(value)
        self.view.setupTab.categoryField.setText(value)

    def _author_list_item_selected(self, value):
        if value == 0:
            value = ""
        else:
            value = self.view.setupTab.authorList.itemText(value)
        self.view.setupTab.authorField.setText(value)

    def _tag_button_toggled(self, button, checked):
        value = button.text()
        value = "!#@%!".join(value.split("&&"))
        value = value.replace("&", "")
        value = value.replace("!#@%!", "&")
        if checked:
            self.post_model.add_tag(value)
        else:
            self.post_model.remove_tag(value)

    def _set_tags_group(self):
        values = self.view.setupTab.tagField.text()
        separator = ","
        if ";" in values:
            separator = ";"

        for tag in values.split(separator):
            tag = tag.strip()
            if not tag:
                continue
            if tag not in self.known_metadata_model.tags:
                self.known_metadata_model.tags.append(tag)
            self.post_model.add_tag(tag)

        self.view.setupTab.tagField.clear()
        known_tags = ["&&".join(x.split("&")) for x in sorted(self.known_metadata_model.tags)]
        checked_tags = ["&&".join(x.split("&")) for x in self.post_model.tags]
        self.view.setupTab.setTagButtons(known_tags, checked_tags)

    def _set_combobox_values(self, qcombobox, values):
        new_values = ["Pick value"]
        new_values.extend(sorted(values, key=str.lower))
        qcombobox.clear()
        qcombobox.addItems(new_values)

    def _update_view_options_based_on_metadata(self):
        self.view.saveFileDialog.setDirectory(self.known_metadata_model.path)
        self._set_tags_group()
        self._set_combobox_values(
            self.view.setupTab.categoryList, self.known_metadata_model.category
        )
        self._set_combobox_values(self.view.setupTab.authorList, self.known_metadata_model.authors)
