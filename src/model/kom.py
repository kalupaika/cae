#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""© Ihor Mirzov, 2019-2021
Distributed under GNU General Public License v3.0

CalculiX Keyword Object Model (hierarchy).
Parser supposts mutually exclusive parameters for keywords.
Keywords with all arguments are parsed from config/kom.xml.
On INP import KOM is enriched with keyword implementations.
"""

# Standard modules
import os
import sys
import logging
from enum import Enum
import xml.etree.ElementTree as ET

# My modules
sys_path = os.path.abspath(__file__)
sys_path = os.path.dirname(sys_path)
sys_path = os.path.join(sys_path, '..')
sys_path = os.path.normpath(sys_path)
sys_path = os.path.realpath(sys_path)
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)
from path import p
from settings import s


class KeywordObjectModel:
    """Implements a chierarchy of all CalculiX keywords."""

    def __init__(self, kom_xml=p.kom_xml):
        """Read CalculiX keywords hierarchy."""

        # List of all existing keywords
        self.keywords = []
        self.keyword_names = ()

        # 'Model' group from kom.xml
        self.root = Group()

        # Parse keywords hierarchy and build Keyword Object Model
        try:
            t = ET.parse(kom_xml)
            self.build(t.getroot(), self.root)
            logging.info('Keywords object model generated.')
        except:
            import traceback
            msg = 'Can\'t generate keywords object model!\n' \
                + traceback.format_exc()
            logging.error(msg)

    def build(self, xml_branch, parent):
        """Recursively build Keyword Object Model."""
        for xml_child in xml_branch:
            logging.log(5, xml_child.tag + ', ' + str(xml_child.attrib))
            """
            xml_child.tag, xml_child.attrib:

            Keyword, {'name': '*RESTART'}
            Keyword, {'name': '*TIME POINTS'}
            Group, {'name': 'Interactions'}
            Group, {'name': 'Constraints'}
            """

            # Create item: group, keyword or argument
            klass = globals()[xml_child.tag]
            item = klass()
            parent.items.append(item)

            # Set fields for object
            setattr(item, 'parent', parent) # set parent
            for k,v in xml_child.attrib.items():
                setattr(item, k, v)

            # Fill self.keywords
            if xml_child.tag=='Keyword':
                self.keywords.append(item)
                self.keyword_names += (item.name, )

            # Argument values for QComboBox
            if xml_child.tag=='Argument' and xml_child.text:
                values = xml_child.text.strip()
                if len(values):
                    values = values.split('|')
                    item.items.extend(values)

            self.build(xml_child, item)

    def get_keyword_by_name(self, name, parent=None):
        """Get keyword from self.keywords by its name."""
        for kw in self.keywords:
            if kw.name == name:
                return kw

    def get_inp_code_as_lines(self, parent=None, level=0):
        """Recursively get whole model inp_code as list of strings (lines).
        Parent is item, level defines code folding/padding.
        """
        lines = []
        if not parent:
            parent = self.root
        if parent.itype == ItemType.IMPLEMENTATION:
            level += 1

        # For each group/keyword from KOM
        for item in parent.items:
            if item.itype == ItemType.ARGUMENT:
                continue
            if item.itype == ItemType.IMPLEMENTATION:

                # inp_code is stripped
                for line in item.inp_code:
                    if line.upper().startswith(self.keyword_names):
                        padding = ' '*4*level
                    else:
                        padding = ' '*4*(level+1)
                    if line.startswith('**'):
                        padding = ''
                    lines.append(padding + line + '\n')

            # Continue call iterator until dig to implementation
            lines.extend(self.get_inp_code_as_lines(item, level))

        return lines

    def get_top_keyword_by_name(self, parent, kw_name):
        kw = None
        for item in parent.items:
            if item.itype == ItemType.ARGUMENT:
                continue
            if item.itype == ItemType.KEYWORD \
                and item.name == kw_name.upper():
                return item
            else:
                kw = self.get_top_keyword_by_name(item, kw_name)
                if kw is not None:
                    return kw


class ItemType(Enum):
    """Enums for 'itype' variable."""
    GROUP = 0
    KEYWORD = 1
    ARGUMENT = 2
    IMPLEMENTATION = 3


class Item:
    """Needed for inheritance by further classes."""

    def __init__(self):
        self.itype = ''      # item type: group/keyword/argument/implementation
        self.name = ''       # name of item, string
        self.items = []      # list of children
        self.parent = None   # item parent item
        self.active = False

    def is_active(self):
        """Define if item is active."""

        # Top groups
        if self.parent and self.parent.name == 'Model':
            self.active = True
            return True

        # Children of active groups
        elif self.parent and self.parent.active and self.parent.itype in \
            [ItemType.GROUP, ItemType.IMPLEMENTATION]:
            self.active = True
            return True

        # Implementations are always active
        elif self.itype == ItemType.IMPLEMENTATION:
            self.active = True
            return True

        else:
            self.active = False
            return False

    def copy_items_to(self, another_item):
        """Recursively copy tree branch to implementation."""
        import copy
        another_item.items = []
        for item in self.items:
            if item.itype in [ItemType.GROUP, ItemType.KEYWORD]:
                copied_item = copy.copy(item) # newer use deepcopy!
                copied_item.parent = another_item
                copied_item.active = True
                another_item.items.append(copied_item)
                item.copy_items_to(copied_item)
            if item.itype == ItemType.ARGUMENT:
                copied_item = copy.copy(item)
                another_item.items.append(copied_item)

    def count_implementations(self):
        """Recursive function to count keyword
        implementations in item descendants.
        """
        if self.itype == ItemType.ARGUMENT:
            return 0

        counter = 0
        for i in self.items:
            if i.itype == ItemType.IMPLEMENTATION:
                counter += 1
            else:
                counter += i.count_implementations()
        return counter

    def get_implementations(self):
        """Get list of keywords implementations."""
        imps = []
        for item in self.items:
            if item.itype == ItemType.IMPLEMENTATION:
                imps.append(item)
        return imps

    def get_child_by_name(self, name):
        """Search item by name among children."""
        for item in self.items:
            if item.name == name:
                return item

    def get_parent_keyword_name(self):
        """Returns first active preceding/parent keyword (not group)."""
        if (self.parent.itype == ItemType.KEYWORD or \
            self.parent.name == 'Model') and self.parent.active:
                return self.parent.name
        else:
            return self.parent.get_parent_keyword_name()

    def get_path(self):
        """Get item path bottom-upwards."""
        parents = []
        while self.parent is not None: # root has None parent
            parents.insert(0, self)
            self = self.parent
        parents.insert(0, self) # insert root
        return [p.name for p in parents]


class Group(Item):
    """Group of keywords, like 'Properties', 'Constraints', etc."""

    def __init__(self):
        super().__init__()
        self.itype = ItemType.GROUP
        self.items = [] # list of groups and keywords
        self.name = 'Model' # default name (root group)
        self.expanded = s.expanded


class Keyword(Item):
    """*AMPLITUDE, *BOUNDARY, *STEP etc."""

    def __init__(self):
        super().__init__()
        self.itype = ItemType.KEYWORD
        self.items = [] # list of arguments
        self.name = ''
        self.from_new_line = False # start all arguments from the next line?
        self.expanded = s.expanded


class Argument(Item):
    """Keyword argument."""

    def __init__(self):
        super().__init__()
        self.itype = ItemType.ARGUMENT
        self.items = [] # list of strings
        self.name = ''
        self.form = '' # QCheckBox, QLineEdit, QComboBox
        self.required = False


class Implementation(Item):
    """Keyword implementation - 
    a piece of INP-code for CalculiX input file.
    """

    def __init__(self, keyword, inp_code, name=None):
        super().__init__()

        self.itype = ItemType.IMPLEMENTATION
        keyword.copy_items_to(self)
        self.parent = keyword
        self.active = True
        self.expanded = s.expanded

        # Name of current implementation (of *AMPLITUDE, *STEP, *MATERIAL etc.)
        index = len(self.parent.get_implementations())
        if name:
            self.name = name # it will be used in edit Dialog
        else:
            i = 0
            while inp_code[i].startswith('**'):
                i += 1
            lead_line = inp_code[i]

            import re
            match = re.search('(NAME|ELSET|NSET)\s*=\s*([\w\!\#\%\$\&\"\'\(\)\*\=\+\-\.\/\:\;\<\>\?\@\[\]\^\_\`\{\\\|\}\~]*)', lead_line.upper())
            if match:
                self.name = lead_line[match.start(2):match.end(2)]
            else:
                self.name = self.parent.name[1:] + '-' + str(index + 1)

        self.inp_code = inp_code # INP-code for current implementation - list of strings
        self.parent.items.insert(index, self) # append implementation to keyword items
        if name:
            logging.info('{} \"{}\" updated.'.format(keyword.name, self.name))
        else:
            logging.info('{} {} created.'.format(keyword.name, self.name))
            # logging.debug(' > '.join(self.get_path()))


# Empty Keyword Object Model w/o implementations
logging.disable() # switch off logging
KOM = KeywordObjectModel()
logging.disable(logging.NOTSET) # switch on logging
