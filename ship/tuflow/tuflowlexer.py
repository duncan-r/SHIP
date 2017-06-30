'''
Example functions for simplified parsing of a tuflow control file
into objects

TODO: Needs integrating with the rest of SHIP
(i.e using ship classes instead of Statement/ControlFileNode or integrating these)
'''
from __future__ import print_function
from ply import lex
from ship.tuflow.containers import ControlFileNode

class Lexer(object):
    '''
    Lexer for tokenising tuflow control files
    '''
    states = (
        ('param', 'inclusive'),
    )

    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'define': 'DEFINE',
        'end': 'END',
    }

    tokens = [
        'COMMAND',
        'PARAMETER',
        'COMMENT',
        'NEWLINE',
        'ASSIGNMENT',
    ] + list(reserved.values())

    t_ignore = " \t"
    t_COMMENT = r'[#!].*'

    def t_ASSIGNMENT(self, t):
        r'\=='
        t.lexer.begin('param')

    def t_param_NEWLINE(self, t):
        r'\n+'
        t.lexer.begin('INITIAL')
        t.lexer.lineno += t.value.count("\n")
        return t

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        t.lexer.begin('INITIAL')
        return t

    def t_param_PARAMETER(self, t):
        r'[^!^#^\s]+'
        return t

    def t_COMMAND(self, t):
        r'[\(a-zA-Z_/][a-zA-Z0-9_,\)]*'
        t.type = self.reserved.get(t.value.lower(), 'COMMAND')
        return t

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '{}' on line {}".format(t.value[0], t.lexer.lineno))
        t.lexer.skip(1)

    def build(self, **kwargs):
        '''
        Build the lexer
        '''
        self.lexer = lex.lex(module=self, **kwargs)

class Parser(object):
    '''
    Parser for tuflow control files
    Accepts a token stream from Lexer and creates
    container objects
    '''
    def __init__(self, lexer, keep_comments=True):
        self.lexer = lexer
        self.keep_comments = keep_comments
        self.command = []
        self.parameter = []
        self.comment = None
        self.keyword = []

    def parse(self, container):
        '''
        Parses a tuflow control file, placing the results in
        ``container``.

        Args:
            container (ControlFileNode): The root node to begin parsing with.

        E.g.
        container = ControlFileNode('ROOT')
        parse(lexer, container)
        '''
        try:
            while True:
                token = self.lexer.token()
                if not token:
                    break
                if token.type in ('IF', 'DEFINE'):
                    container.append(self.parse(ControlFileNode(token.type, keyword=token.type)))
                elif token.type == 'END':
                    self._end(token)
                elif token.type == 'ELSE':
                    self._else()
                elif token.type == 'NEWLINE':
                    self._newline(container)
                elif token.type == 'COMMENT':
                    self.comment = token.value
                elif token.type == 'PARAMETER':
                    self.parameter.append(token.value)
                elif token.type == 'COMMAND':
                    self.command.append(token.value)
        except StopIteration:
            pass
        return container

    def _else(self):
        self.keyword.append('ELSE')
        # consume next token
        token = self.lexer.token()
        # if it is not an 'IF' we have another statment
        # otherwise ignore
        if token.type == 'COMMAND':
            self.command.append(token.value)
        elif token.type == 'IF':
            self.keyword.append(token.type)

    def _newline(self, container):
        if self.command or self.parameter:
            container.append(
                ControlFileNode(
                    'STATEMENT',
                    command=" ".join(self.command),
                    parameter=" ".join(self.parameter),
                    comment=self.comment,
                    keyword=" ".join(self.keyword)
                )
            )
            self.command = []
            self.parameter = []
            self.keyword = []
            self.comment = None
        elif self.comment and self.keep_comments:
            container.append(ControlFileNode('COMMENT', comment=self.comment))
            self.comment = None

    def _end(self, token):
        # look ahead to next token
        next_tok = self.lexer.token()

        # If it is an 'if' or 'define', we are at the end
        # of this control block, so we should break out of lexing
        if next_tok.type in ('IF', 'DEFINE'):
            raise StopIteration
        else:
            # Some other commands actually start with 'END' (!)
            self.command.append(token.value)
            self.command.append(next_tok.value)

def loadFile(tcf_path, keep_comments=True):
    '''
    Read a file into a ControlFileNode
    '''
    with open(tcf_path) as fin:
        source = fin.read()
    lexer = Lexer()
    lexer.build()
    lexer.lexer.input(source)
    parser = Parser(lexer.lexer, keep_comments=True)
    return parser.parse(ControlFileNode('ROOT'))
