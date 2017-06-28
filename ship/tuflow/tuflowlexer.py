'''
Example functions for simplified parsing of a tuflow control file
into objects

TODO: Needs integrating with the rest of SHIP
(i.e using ship classes instead of Statement/ControlStructure or integrating these)
'''
from __future__ import print_function
from ply import lex
from ship.tuflow.containers import Statement, ControlStructure

class TuflowLexer(object):
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
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value.lower(), 'COMMAND')
        return t

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def build(self, **kwargs):
        '''
        Build the lexer
        '''
        self.lexer = lex.lex(module=self, **kwargs)

def parse(lexer, container, keep_comments=True):
    '''
    Parses a tuflow control file, placing the results in
    ``container``.
    ``container`` can be any object which provides an ``append``
    method.
    E.g.
    container = ControlStructure('ROOT')
    parse(lexer, container)
    '''
    command = []
    parameter = []
    comment = None
    while True:
        token = lexer.token()
        if not token:
            break
        if token.type in ('IF', 'DEFINE'):
            container.append(parse(lexer, ControlStructure(token.type), keep_comments))
        elif token.type == 'END':
            # look ahead to next token
            next_tok = lexer.token()

            # If it is an 'if' or 'define', we are at the end
            # of this control block, so we should break out of lexing
            if next_tok.type in ('IF', 'DEFINE'):
                break
            else:
                # Some other commands actually start with 'END' (!)
                command.append(token.value)
                command.append(next_tok.value)
        elif token.type == 'ELSE':
            # consume next token as it is an 'IF' we can ignore
            lexer.token()
        elif token.type == 'NEWLINE':
            if command or parameter:
                container.append(
                    Statement(" ".join(command), " ".join(parameter), comment)
                )
                command, parameter, comment = [], [], None
            elif comment and keep_comments:
                container.append(Statement(comment=comment))
                comment = None
        elif token.type == 'COMMENT':
            comment = token.value
        elif token.type == 'PARAMETER':
            parameter.append(token.value)
        elif token.type == 'COMMAND':
            command.append(token.value)
    return container

def loadFile(tcf_path, keep_comments=True):
    '''
    Read a file into a ControlStructure
    '''
    with open(tcf_path) as fin:
        source = fin.read()
    lexer = TuflowLexer()
    lexer.build()
    lexer.lexer.input(source)
    return parse(lexer.lexer, ControlStructure('ROOT'), keep_comments)
