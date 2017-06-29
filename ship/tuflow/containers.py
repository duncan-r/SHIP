from ship.tuflow.tuflowmodel import TuflowFilepartTypes

class Statement(object):
    '''
    A single tuflow statement, of the form COMMAND == PARAMETER.
    Also keeps the original comment
    '''

    def __init__(self, command=None, parameter=None, comment=None):
        self.command = command
        self.comment = comment
        self.parameter = parameter
        self.__type = None

    def __repr__(self):
        return "<Statement: {}>".format(self.command or 'Comment')

    def __str__(self):
        if not self.command:
            return self.comment
        return "{} == {} {}".format(self.command, self.parameter, self.comment)

    @property
    def type(self):
        '''
        Returns the filepart type of this statement
        '''
        if not self.__type and self.command:
            _, self.__type = TuflowFilepartTypes().find(self.command)
        return self.__type


class ControlStructure(object):
    '''
    A container for a control structure within a tuflow control file.
    3 types of structure are defined:
    ROOT: The entire file
    IF: An if-block which can contain multiple 'ELSE IF' statements
    DEFINE: A 'DEFINE' block which can contain multiple statements.

    An instance of ``ControlStructure`` is essentially just a grouping of
    ``Statement`` instances
    '''

    logic_types = {'ROOT', 'IF', 'DEFINE'}

    def __init__(self, logic_type, statements=None):
        if logic_type not in self.logic_types:
            raise TypeError(
                'logic_type must be one of {}'.format(self.logic_types))
        self.logic_type = logic_type
        self.statements = statements or []
        self.__type = None

    def __repr__(self):
        return "<ControlStructure: {}>".format(self.logic_type)

    def __str__(self):
        writer = getattr(self, "_write_{}_block".format(
            self.logic_type.lower()))
        return writer()

    @property
    def type(self):
        '''
        Returns the filepart type of this logical block.
        If this is the root block (i.e. the whole file)
        then it will return none
        '''
        if not self.__type and len(self.statements) > 0:
            _, self.__type = TuflowFilepartTypes().find(
                "{} {}".format(self.logic_type, self.statements[0].command)
            )
        return self.__type

    def _write_root_block(self):
        '''
        A root block contains the entire control file
        '''
        return "\n".join((st.__str__() for st in self.statements))

    def _write_if_block(self):
        '''
        Statements are formatted in an IF...ELSE IF...END IF
        control structure
        '''
        first = self.statements[0]
        second = self.statements[1]
        out = 'IF {}\n\t{}\n'.format(first.__str__(), second.__str__())
        for i in range(2, len(self.statements) - 1):
            out += 'ELSE IF {}\n\t{}\n'.format(
                self.statements[i].__str__(), self.statements[i + 1].__str__())
        out += 'END IF'
        return out

    def _write_define_block(self):
        '''
        Statements are formatted in a DEFINE....END DEFINE
        control structure
        '''
        return 'DEFINE {}\n{}\nEND DEFINE'.format(
            self.statements[0].__str__(),
            "\n\t".join(st.__str__() for st in self.statements[1:]))

    def append(self, statement):
        '''
        Append a Statement or another ControlStructure.
        '''
        if not isinstance(statement, (Statement, ControlStructure)):
            raise TypeError(
                "Can only append Statement or ControlStructure types")
        self.statements.append(statement)
