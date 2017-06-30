from ship.tuflow.tuflowmodel import TuflowFilepartTypes


class ControlFileNode(object):
    '''
    A container for a control structure within a tuflow control file.
    3 types of structure are defined:
    ROOT: The entire file
    IF: An if-block which can contain multiple 'ELSE IF' statements
    DEFINE: A 'DEFINE' block which can contain multiple statements.

    An instance of ``ControlFileNode`` is essentially just a grouping of
    ``Statement`` instances
    '''

    node_types = {'ROOT', 'IF', 'DEFINE', 'STATEMENT', 'COMMENT'}

    def __init__(
            self,
            node_type,
            command=None,
            parameter=None,
            comment=None,
            keyword=None,
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

        # Keywords can be 'IF', 'DEFINE', 'ELSE' or 'ELSE IF'
        # and dictate how to write out this statement
        self.keyword = keyword

        self.__type = None

    def __repr__(self):
        return "<ControlFileNode: {}>".format(self.node_type)

    def __str__(self):
        writer = getattr(self, "_write_{}_block".format(
            self.node_type.lower()))
        return writer()

    @property
    def indent(self):
        if self.node_type in {'IF', 'DEFINE'}:
            return '\t'
        return ''

    @property
    def type(self):
        '''
        Returns the filepart type of this logical block.
        If this is the root block (i.e. the whole file)
        then it will return none
        '''
        if not self.__type:
            if self.node_type == 'STATEMENT':
                _, self.__type = TuflowFilepartTypes().find(self.command)
            elif self.node_type in {'IF', 'DEFINE'}:
                _, self.__type = TuflowFilepartTypes().find(
                    "{} {}".format(self.node_type, self.children[0].command)
                )
        return self.__type

    def _write_root_block(self):
        '''
        A root block contains the entire control file
        '''
        return "\n".join((st.__str__() for st in self.children))

    def _write_if_block(self):
        '''
        Statements are formatted in an IF...ELSE IF...END IF
        control structure
        '''
        first = self.children[0]
        newline = "\n{indent}".format(indent=self.parent.indent)
        out = '{indent}IF {first}\n{block}{newline}END IF'.format(
            first=first.__str__(),
            block=newline.join(st.__str__() for st in self.children[1:]),
            newline=newline,
            indent=self.parent.indent
        )
        return out

    def _write_define_block(self):
        '''
        Statements are formatted in a DEFINE....END DEFINE
        control structure
        '''
        return 'DEFINE {}\n\t{}\nEND DEFINE'.format(
            self.children[0].__str__(),
            "\n".join(st.__str__() for st in self.children[1:]))

    def _write_statement_block(self):
        '''
        Writes the statement of this node
        '''
        line = ''
        if self.keyword:
            line += self.keyword
            if self.keyword == 'ELSE':
                line += '\n'
        if self.command:
            line += ' ' + self.command
        if self.parameter:
            line += ' == ' + self.parameter
        if self.comment:
            line += ' ' + self.comment
        return line

    def _write_comment_block(self):
        return self.comment

    def root(self):
        if self.parent:
            return self.parent.root()
        else:
            return self

    def append(self, node):
        '''
        Append a Statement or another ControlFileNode.
        '''
        if not isinstance(node, ControlFileNode):
            raise TypeError(
                "Can only append ControlFileNode types")
        node.parent = self
        self.children.append(node)

    def walk(self):
        '''
        Depth-first traversal of the tree
        '''
        for node in self.children:
            yield node
            if node.children:
                for node in node.walk():
                    yield node

    def filter(self, part_type, unique=True):
        '''
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
