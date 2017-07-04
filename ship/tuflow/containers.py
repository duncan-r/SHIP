from __future__ import print_function
import os
import sys
from ship.tuflow.tuflowmodel import TuflowFilepartTypes
from ship.tuflow import FILEPART_TYPES as fpt

class ControlFileNode(object):
    '''A container for a tuflow control file node.
    3 types of structure are defined:
    ROOT: The entire file
    IF: An if-block which can contain multiple 'ELSE IF' statements
    DEFINE: A 'DEFINE' block which can contain multiple statements.

    An instance of ``ControlFileNode`` is essentially just a grouping of
    ``Statement`` instances
    '''

    node_types = {'ROOT', 'KEYWORD', 'STATEMENT', 'COMMENT'}
    logic_commands = {'IF', 'DEFINE'}

    def __init__(
            self,
            node_type,
            command=None,
            parameter=None,
            comment=None,
            parent=None
    ):
        if node_type not in self.node_types:
            raise TypeError(
                'logic_type must be one of {}'.format(self.node_types))
        self.node_type = node_type
        self.parent = parent
        self.children = []

        # Command is anything (excluding keywords) on the LHS of '=='
        self.command = command

        # A comment (preceded by ! or #) at the end of the line
        self.comment = comment

        # Parameter is anything (excluding a comment) on the RHS of '=='
        self.parameter = parameter

        self.__type = None

    def __repr__(self):
        return "<ControlFileNode: {}>".format(self.node_type)

    def __str__(self):
        line = ''
        if self.command:
            line += self.command + ' '
        if self.parameter:
            line += '== %r ' % self.parameter
        if self.comment:
            line += self.comment

        if self.command in {'IF', 'ELSE IF'}:
            # No newline as next command needs to be on same
            # line
            return line
        return line + '\n'

    @property
    def parameter_options(self):
        '''Split parameters into their options
        Yields the parameters, splitting them by the |
        separator and stripping whitespace
        '''
        for parameter in self.parameter.split('|'):
            yield parameter.strip()

    @property
    def type(self):
        '''filepart type of this node.
        If this is the root block or a keyword such as ELSE/ELSE IF
        then it will return none
        '''
        if not self.__type:
            if self.node_type == 'STATEMENT':
                _, self.__type = TuflowFilepartTypes().find(self.command)
            elif self.node_type == 'KEYWORD' and self.children:
                _, self.__type = TuflowFilepartTypes().find(
                    "{} {}".format(self.command, self.children[0].command)
                )
        return self.__type

    def root(self):
        '''Find the root node of the tree
        '''
        if self.parent:
            return self.parent.root()
        else:
            return self

    def append(self, node):
        '''Append a node

        Args:
            node (ControlFileNode): The node to append to this one
        '''
        if not isinstance(node, ControlFileNode):
            raise TypeError(
                "Can only append ControlFileNode types")
        node.parent = self
        self.children.append(node)

    def append_statement(self, command, parameter, comment=None):
        '''Append a statement to the tree
        '''
        node = ControlFileNode(command, parameter, comment)
        if self.command in self.logic_commands:
            # We must append it before the last node which is the 'END' node
            node.parent = self
            self.children.insert(-1, node)
        else:
            self.append(node)

    def walk(self):
        '''Depth-first traversal of the tree
        '''
        for node in self.children:
            yield node
            if node.children:
                for node in node.walk():
                    yield node

    def filter(self, part_type, unique=True):
        '''Filter nodes by filepart types
        Generator which yields all statements which have a type equal
        to the given filepart type

        Args:
            part_type: One of the FILEPART_TYPES enum or an iterable (set, tuple or list) of
                FILEPART_TYPES to filter against

            unique (bool): Specifies whether to ignore duplicate commands

        Yields:
            Statement: A control file statement matching the filepart_type
        '''
        if not isinstance(part_type, (list, set, tuple)):
            part_type = {part_type}

        commands = set()
        for node in self.walk():
            if node.type in part_type:
                if not unique:
                    yield node
                elif node.command not in commands:
                    commands.add(node.command)
                    yield node

    def write(self, indent_char="  ", out=sys.stdout):
        '''Pretty print the tree, starting at the current node

        Args:
            indent_char (str): The character string to use as an indent. Defaults to 2 spaces
            out (file): File-like object which supports a `write` method. Defaults to stdout
        '''
        scopingCommands = {'IF', 'DEFINE'}
        scope_count = 0
        for node in self.walk():
            # Count when we enter a control block
            if node.command in scopingCommands:
                scope_count += 1

            # The indent level is dependent on the number of
            # nested blocks we are (scope_count) and the type
            # of node. If the node is a keyword, we only indent
            # to the 'outer' scope level. If if is the first child
            # of the start of the block (i.e the IF keyword),
            # we dont indent as this has to be on the same line
            if node.parent.children[0] is node:
                indent_level = 0
            elif node.node_type == 'KEYWORD':
                indent_level = scope_count - 1
            else:
                indent_level = scope_count

            # Write the line
            indent = indent_char * indent_level
            line = indent + str(node)
            out.write(line)

            # Check whether we need to leave this scope
            if node.node_type == 'KEYWORD' and 'END' in node.command:
                scope_count -= 1


class Model(object):
    '''Represents a tuflow model
    '''
    def __init__(self, root, control_file_tree):
        self._root = root
        self.control_file_tree = control_file_tree

    @property
    def root(self):
        '''The root directory of the control file
        '''
        return self._root

    def checkPathsExist(self):
        '''Check all input filepaths in the model exist

        Yields:
            ControlFileNode: A node whose parameter is a missing path
        '''
        for node in self.control_file_tree.filter({fpt.MODEL, fpt.GIS, fpt.DATA}):
            for path in node.parameter_options:
                if not os.path.isabs(path):
                    path = os.path.normpath(os.path.join(self._root, path))
                if not os.path.exists(path):
                    yield node, path
