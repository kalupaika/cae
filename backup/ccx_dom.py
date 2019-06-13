# -*- coding: utf-8 -*-

"""
    © Ihor Mirzov, UJV Rez, June 2019.
    Distributed under GNU General Public License, version 2.

    Data object model based on CalculiX keywords hierarchy.
    Keywords with all arguments are parsed from ccx_dom.txt.
    Parser supposts mutually exclusive parameters for keywords.
"""


# CalculiX keywords hierarchy - data object model
class DOM:

    # Read CalculiX keywords hierarchy
    def __init__(self):

        # Last parent for given padding level
        parent_items = {}

        # Analyze keywords hierarchy
        with open('ccx_dom.txt', 'r') as f:
            for line in f.readlines(): # read the whole file and iterate over line

                # Skip comments and empty lines
                if line.strip() == '': continue 
                if line.strip().startswith('**'): continue

                # Define padding level
                level = 0 # level of current item = amount of tabs
                line = line.rstrip() # cut '\n'
                while line.startswith('\t'):
                    level += 1
                    line = line[1:] # cut 1 tab

                # Define item for current padding level
                if line.startswith('*'):
                    item = keyword(line, level)
                elif line.startswith(','):
                    item = argument(line, level)
                elif line.endswith('__group'):
                    item = group(line, level)

                # Update parent item
                parent_items[level] = item
                if level > 0:
                    parent_items[level-1].addItem(item)

        self.root = parent_items[0] # group 'Model'


# Group of keywords, like 'Properties', 'Constraints', etc.
class group:

    item_type = 'group' # needed to distinguish from 'keyword'
    implementations = [] # will always be empty

    def __init__(self, line, level):
        line = line.strip().replace('__group', '')
        self.name = line
        self.items = [] # list of groups and keywords
        self.level = level # needed for padding in printAll()

    def addItem(self, item):
        self.items.append(item)
    
    def printAll(self):
        string = '\t' * self.level
        string += self.name
        # print(string)
        for item in self.items:
            string += item.printAll()
        return string


# *AMPLITUDE, *BOUNDARY, *STEP etc.
class keyword:

    item_type = 'keyword' # needed to distinguish from 'group'

    def __init__(self, line, level):
        line = line.strip()

        # Start all arguments from the next line?
        self.from_new_line = False # marks that argument should be printed from the new line
        if '__newline' in line:
            self.from_new_line = True # yes
            line = line.replace('__newline', '')

        self.name = line
        self.items = [] # list of groups, keywords and arguments
        self.level = level # needed for padding in printAll()
        self.implementations = [] # list of INP_codes generated via keyword dialog

    def addItem(self, item):
        self.items.append(item)

    def printAll(self):
        string = self.name + '\n'
        for impl in self.implementations:
            string += impl.name + '\n'
        for item in self.items:
            if item.item_type != 'argument':
                continue
            string += item.printAll()
        return string


# Keyword's argument
class argument:

    """
        name            - argument's name
        required        - required or optional
        values          - list of possible values
        level           - padding level in ccx_dom.txt
    """
    items = [] # do not remember why, but it's needed
    item_type = 'argument' # needed to distinguish from 'group' and 'keyword'

    def __init__(self, line, level):

        self.level = level # needed for padding in printAll()
        line = line[1:] # cut comma

        # Required or optional
        self.required = False
        if '__required' in line:
            self.required = True

        self.values = [] # list of strings
        left_part = line
        if '=' in line:
            # arguments : values
            left_part, right_part = line.split('=')
            left_part = left_part + '='

            # Define argument's values
            # TODO add '+' splitter for arguments that always go together
            if '|' in right_part:
                # if few values are present
                self.values = [v for v in right_part.split('|')]
            elif len(right_part):
                # one value only
                self.values = [right_part]

        # If '__required' is present - remove it
        if '__required' in left_part:
            left_part = left_part.replace('__required', '')

        # Define argument's name
        self.name = left_part


    def printAll(self):
        string = ',' + self.name

        if self.required:
            string += '__required'

        amount_of_values = len(self.values)
        if amount_of_values:
            # string += ':'
            for i in range(amount_of_values-1):
                string += self.values[i] + '|'
            string += self.values[amount_of_values-1]

        return string + '\n'


# Keyword implementation - a piece of INP-code for CalculiX input file
class implementation:

    item_type = 'implementation' # needed to distinguish from 'group' and 'keyword'

    def __init__(self, keyword, INP_code):
        # Name of current implementation (of *AMPLITUDE, *STEP, *MATERIAL etc.)
        self.name = keyword.name[1:]+'-'+str(len(keyword.implementations)+1)
        self.INP_code = INP_code # INP-code for current implementation - list of strings
        keyword.implementations.append(self)


# Parses whole the input file or INP-code pieces from keyword's implementation
class Parse:

    def __init__(self, INP_code):
        for line in INP_code:
            pass