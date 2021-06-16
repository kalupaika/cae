#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" © Ihor Mirzov, 2019-2021
Distributed under GNU General Public License v3.0

Dialog window to create/edit keyword implementation.
Called via double click on keyword in the treeView.
Here we define a keyword implementation: its name and inp_code.
It is created via Factory class, run_master_dialog() method.
So this dialog is a master, help webbrowser is a slave. """

# Standard modules
import os
import sys
import re
import math
import logging

# External modules
from PyQt5 import QtWidgets, uic, QtCore, QtGui, QtWebEngineWidgets

# My modules
sys_path = os.path.abspath(__file__)
sys_path = os.path.dirname(sys_path)
sys_path = os.path.join(sys_path, '..')
sys_path = os.path.normpath(sys_path)
sys_path = os.path.realpath(sys_path)
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)
import tests
import path
import settings
import gui
import gui.window
from model.kom import ItemType, KOM


# Load HTML help into QWebEngineView
# TODO Compare with doc.py/save_html()
def save_html(item):
    USE_CACHED_HTML = True # if False cached html will NOT be used

    # Get keyword name
    if item.itype == ItemType.KEYWORD:
        keyword_name = item.name[1:] # cut star
    if item.itype == ItemType.IMPLEMENTATION:
        keyword_name = item.parent.name[1:] # cut star

    # Avoid spaces in html page names
    html_page_name = keyword_name.replace(' ', '_')

    url = os.path.join(path.p.doc, html_page_name + '.html')

    # Generate html file if it wasn't created previously
    if not os.path.isfile(url) or not USE_CACHED_HTML:

        # Open 'ccx.html' and find link to keyword's page
        href = 'ccx.html'
        with open(os.path.join(path.p.doc, href), 'r') as f:
            for line in f.readlines():
                match = re.search('node\d{3}\.html.{3}' + keyword_name, line) # regex to match href
                if match:
                    href = match.group(0)[:12]
                    break

        # Read html of the keyword page
        html = '<html><head><link rel="stylesheet" type="text/css" href="style.css"/></head><body>'
        with open(os.path.join(path.p.doc, href), 'r') as f:
            append = False
            cut_breakline = True
            for line in f.readlines():
                if '<!--End of Navigation Panel-->' in line:
                    append = True
                    continue
                if '<HR>' in  line:
                    break
                if '<PRE>' in line:
                    cut_breakline = False
                if '</PRE>' in line:
                    cut_breakline = True
                if append:
                    if cut_breakline:
                        line = line[:-1] + ' ' # replace '\n' with space
                    html += line
        html += '</body></html>'
        html = re.sub('<A.+?\">', '', html) # '?' makes it not greedy
        html = html.replace('</A>', '')
        with open(url, 'w') as f:
            f.write(html)

    return url


class KeywordDialog(QtWidgets.QDialog):

    # Load form and show the dialog
    @gui.window.init_wrapper()
    def __init__(self, args):
        self.info = None # WindowInfo will be set in @init_wrapper
        KOM = args[0]
        self.item = args[1] # needed to pass to other functions
        self.widgets = [] # list of created widgets

        # Load UI form - produces huge amount of redundant debug logs
        logging.disable() # switch off logging
        super().__init__() # create dialog window
        uic.loadUi(path.p.dialog_xml, self) # load empty dialog form
        logging.disable(logging.NOTSET) # switch on logging

        # Align dialog
        if settings.s.align_windows:
            size = QtWidgets.QDesktopWidget().availableGeometry()
            # TODO check this bug in Windows 10
            if os.name == 'nt': # just bug with window border padding
                width = math.floor(size.width() / 3) - 22
                height = size.height() - 55
            else:
                width = math.floor(size.width() / 3)
                height = size.height()
            self.setGeometry(0, 0, width, height)

        # Add window icon (different for each keyword)
        icon_name = self.item.name.replace('*', '') + '.png'
        icon_name = icon_name.replace(' ', '_')
        icon_name = icon_name.replace('-', '_')
        icon_path = os.path.join(path.p.img, 'icon_' + icon_name.lower())
        icon = QtGui.QIcon(icon_path)
        self.setWindowIcon(icon)

        # New implementation: draw full form for keyword arguments
        if self.item.itype == ItemType.KEYWORD:
            self.setWindowTitle('New ' + self.item.name)

            # For each keyword argument create name and value widgets
            row_number = 0 # row number for vertical layout
            for argument in self.item.items:
                if argument.itype != ItemType.ARGUMENT:
                    continue

                argument_values_items = argument.items
                for ag in argument.name.split('|'):
                    logging.debug('\nArgument ' + ag)

                    # Try to get existing implementations for argument.name
                    keyword = KOM.get_keyword_by_name('*' + ag)
                    if keyword is not None:
                        """
                            For example, add names of *AMPLITUDE implementations,
                                if argument.name is 'AMPLITUDE'
                        """
                        argument_values_items = ['']
                        # Example: ELSET argument in *ELSET keyword
                        if ag != self.item.name.upper()[1:]:
                            implementations = [item.name for item in keyword.get_implementations()]
                            logging.debug('\tKeyword ' + keyword.name)
                            logging.debug('\t\tImplementations ' + str(implementations))
                            logging.debug('\t\tArgument items ' + str(argument.items))
                            if len(implementations) and not len(argument.items):
                                argument.form = 'QComboBox'
                                if len(implementations) == 1:
                                    argument_values_items = implementations
                                if len(implementations) > 1:
                                    argument_values_items.extend(implementations)

                # Argument values
                if argument.form == 'QComboBox':
                    argument_name_text = argument.name + '='

                    # Predefined values to be chosen
                    argument_values_widget = QtWidgets.QComboBox()
                    argument_values_widget.addItems(argument_values_items)

                    # Assign event to update textEdit widget
                    argument_values_widget.currentIndexChanged.connect(self.change)

                    # QComboBox doesn't expand by default
                    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                    sizePolicy.setHorizontalStretch(1) # expand horizontally
                    argument_values_widget.setSizePolicy(sizePolicy)

                elif argument.form == 'QLineEdit':
                    argument_name_text = argument.name + '='

                    # Values to be entered
                    argument_values_widget = QtWidgets.QLineEdit()

                    # Assign event to update textEdit widget
                    argument_values_widget.textChanged.connect(self.change)

                elif argument.form == 'QCheckBox':
                    argument_name_text = argument.name + ' ' # shift checkbox a little bit for nice view

                    # Flag to be checked
                    argument_values_widget = QtWidgets.QCheckBox()

                    # Assign event to update textEdit widget
                    argument_values_widget.clicked.connect(self.change)

                # Mark required argument
                if argument.required:
                    argument_required_widget = QtWidgets.QLabel()
                    argument_required_widget.setText('Required:')
                    argument_required_widget.setStyleSheet('color:Red;')
                    self.vertical_layout.insertWidget(row_number, argument_required_widget)
                    row_number += 1 # first time

                # Mutually exclusive arguments
                if '|' in argument.name:
                    argument_name_widget = QtWidgets.QComboBox()
                    if argument.form == 'QCheckBox':
                        arg_names = argument.name.split('|')
                    else:
                        arg_names = [n + '=' for n in argument.name.split('|')]
                    argument_name_widget.addItems(arg_names)

                    # Assign event to update textEdit widget
                    argument_name_widget.currentIndexChanged.connect(self.change)

                else:
                    argument_name_widget = QtWidgets.QLabel()
                    argument_name_widget.setText(argument_name_text)

                # Keep name and values in horizontal layout
                horizontal_layout = QtWidgets.QHBoxLayout()
                horizontal_layout.setContentsMargins(0, 0, 0, 20) # bottom margin
                horizontal_layout.addWidget(argument_name_widget)
                horizontal_layout.addWidget(argument_values_widget)
                horizontal_layout.setAlignment(QtCore.Qt.AlignLeft)

                # Save name and values for processing in self.change()
                self.widgets.append(argument_name_widget)
                self.widgets.append(argument_values_widget)

                # Add widgets to dialog window
                self.vertical_layout.insertLayout(row_number, horizontal_layout)
                row_number += 1 # second time

            # Fill textEdit widget with default keyword configuration
            self.change(None)

        # Edit implementation: draw only textEdit
        if self.item.itype == ItemType.IMPLEMENTATION:
            self.setWindowTitle('Edit ' + self.item.name)
            for line in self.item.inp_code:
                self.textEdit.append(line)

        # Generate html help page from official manual
        self.doc = QtWebEngineWidgets.QWebEngineView()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2) # expand horizontally
        self.doc.setSizePolicy(sizePolicy)

        self.show_hide_help(False) 
        self.show()

    # Update piece of INP-code in the textEdit widget
    def change(self, event):
        arguments = {} # name:value
        for i, widget in enumerate(self.widgets):

            # Get text from widget: argument name and value
            text = '' # clear text from prev. iteration
            if widget.__class__.__name__ == 'QLabel':
                text = widget.text()
            elif widget.__class__.__name__ == 'QLineEdit':
                text = widget.text()
            elif widget.__class__.__name__ == 'QComboBox':
                text = widget.currentText()
            elif widget.__class__.__name__ == 'QCheckBox':
                if widget.isChecked():
                    text = 'QCheckBox'

            # logging.debug('{} {} {}'.format(i, widget.__class__.__name__, text))

            value = '' # clear value from prev. iteration
            if not 'Required' in text:
                if (i % 2) == 0:
                    # Argument name
                    name = text # name is always present
                else:
                    # Argument value
                    value = text

                    # Flag goes without value, only flag name
                    if len(value.strip()):
                        if value == 'QCheckBox':
                            value = ''
                        arguments[name.strip()] = value

        # Generate text for textEdit widget
        if self.item.itype == ItemType.KEYWORD:
            string = self.item.name
            for name, value in arguments.items():
                if self.item.from_new_line:
                    string += '\n' + name + value # argument goes from new line
                else:
                    string += ', ' + name + value # argument goes inline
        if self.item.itype == ItemType.IMPLEMENTATION:
            string = self.item.parent.name

        self.textEdit.setText(string)

    # Reset textEdit widget to initial state
    def reset(self):
        for i, widget in enumerate(self.widgets):
            if (i % 2) == 1: # iterate over values not labels
                if widget.__class__.__name__ == 'QLineEdit':
                    widget.setText('') # empty is default
                elif widget.__class__.__name__ == 'QComboBox':
                    widget.setCurrentIndex(0) # this row is default
                elif widget.__class__.__name__ == 'QCheckBox':
                    widget.setChecked(False) # uncheck is default
        self.change(None)

    # Return piece of created code for the .inp-file
    def ok(self):
        super().accept()
        return self.textEdit.toPlainText().strip().split('\n')

    # Get URL to the local doc page
    def get_help_url(self):
        if self.item.itype == ItemType.KEYWORD:
            keyword_name = self.item.name[1:] # cut star
        if self.item.itype == ItemType.IMPLEMENTATION:
            keyword_name = self.item.parent.name[1:] # cut star

        # Avoid spaces and hyphens in html page names
        html_page_name = re.sub(r'[ -]', '_', keyword_name)
        url = os.path.join(path.p.doc, html_page_name + '.html')
        return url

    # Show / Hide HTML help
    def show_hide_help(self, button_click):
        w = QtWidgets.QDesktopWidget().availableGeometry().width()

        # If called from button click
        if button_click:
            settings.s.show_help = not settings.s.show_help
            settings.s.save()

        # To show or not to show
        if settings.s.show_help:
            url = save_html(self.item)
            self.doc.load(QtCore.QUrl.fromLocalFile(url)) # load help document

            self.setMaximumWidth(w)
            self.setMinimumWidth(w)
            self.horizontal_layout.addWidget(self.doc)
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Help)\
                .setText('Hide help')
        else:
            self.doc.setParent(None) # remove widget
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Help)\
                .setText('Show help')
            self.setMaximumWidth(w/3)
            self.setMinimumWidth(500)


# Run dialog as MasterWindow
# Start webbrowser from it
@tests.test_wrapper()
def test():
    app = QtWidgets.QApplication(sys.argv)
    f = gui.window.Factory()
    logging.disable() # switch off logging
    k = KOM()
    logging.disable(logging.NOTSET) # switch on logging
    i = k.get_keyword_by_name('*NODE')

    # Create and show dialog window
    d = f.run_master_dialog(k, i) # 0 = cancel, 1 = ok
    print(d)

# Run test
if __name__ == '__main__':
    test()
